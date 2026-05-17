import asyncio
import logging
import csv
import io
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from contextlib import asynccontextmanager

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.database.queries import (
    AsyncSessionLocal, init_db, get_user_count, get_new_users_today,
    get_today_video_count, get_today_revenue, engine
)
from bot.database.models import User, VideoGeneration, Payment, Referral
from bot.main import create_dispatcher, setup_logging

logger = logging.getLogger("admin")
security = HTTPBasic()
templates = Jinja2Templates(directory="admin/templates")

bot_task: Optional[asyncio.Task] = None
is_bot_running = False


def check_admin_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = credentials.username == settings.ADMIN_USERNAME
    correct_password = credentials.password == settings.ADMIN_PASSWORD
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot_task, is_bot_running
    setup_logging()
    
    # Ma'lumotlar bazasi jadvallarini yaratish/tekshirish
    await init_db()
    logger.info("Database initialized successfully.")

    # Telegram botni faqat token kiritilganda ishga tushirish (xatoliklarni oldini olish uchun)
    if settings.BOT_TOKEN.strip():
        try:
            from aiogram import Bot
            from aiogram.client.default import DefaultBotProperties
            from aiogram.enums import ParseMode
            
            bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
            dp = create_dispatcher(settings)
            
            async def run_bot():
                global is_bot_running
                try:
                    is_bot_running = True
                    logger.info("Starting Telegram Bot polling...")
                    await dp.start_polling(bot)
                except Exception as e:
                    logger.error(f"Error in Telegram Bot task: {e}")
                finally:
                    is_bot_running = False

            bot_task = asyncio.create_task(run_bot())
            logger.info("Telegram bot task created successfully in the background.")
        except Exception as e:
            logger.error(f"Failed to start Telegram Bot background task: {e}")
    else:
        logger.warning("BOT_TOKEN is empty! Telegram Bot polling skipped (Maintenance Mode).")

    yield

    # O'chish jarayonida orqa fon vazifalarini to'xtatish
    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
        logger.info("Telegram Bot task cancelled.")


app = FastAPI(
    title="VideoAI Bot Admin Panel",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None
)


@app.get("/health")
async def health():
    """Railway healthcheck uchun endpoint"""
    return {
        "status": "ok",
        "maintenance_mode": settings.is_maintenance,
        "bot_running": is_bot_running,
        "database": "connected"
    }


@app.get("/", response_class=HTMLResponse)
async def redirect_to_admin():
    return RedirectResponse(url="/admin")


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    username: str = Depends(check_admin_credentials)
):
    async with AsyncSessionLocal() as session:
        # Asosiy statistikalar
        total_users = await get_user_count(session)
        new_users_today = await get_new_users_today(session)
        today_videos = await get_today_video_count(session)
        today_rev = await get_today_revenue(session)
        
        # Jami tushum
        result_total_rev = await session.execute(
            select(func.sum(Payment.amount)).where(Payment.status == "confirmed")
        )
        total_revenue = result_total_rev.scalar() or Decimal("0.00")
        
        # Jami muvaffaqiyatli videolar
        result_total_videos = await session.execute(
            select(func.count(VideoGeneration.id)).where(VideoGeneration.status == "done")
        )
        total_videos = result_total_videos.scalar() or 0

        # Oxirgi 10 foydalanuvchi
        result_recent_users = await session.execute(
            select(User).order_by(desc(User.created_at)).limit(10)
        )
        recent_users = result_recent_users.scalars().all()

        # Oxirgi 5 ta to'lov
        result_recent_payments = await session.execute(
            select(Payment).order_by(desc(Payment.created_at)).limit(5)
        )
        recent_payments = result_recent_payments.scalars().all()
        
        # Oxirgi 5 ta video yaratish jarayoni
        result_recent_gens = await session.execute(
            select(VideoGeneration).order_by(desc(VideoGeneration.created_at)).limit(5)
        )
        recent_gens = result_recent_gens.scalars().all()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "username": username,
            "total_users": total_users,
            "new_users_today": new_users_today,
            "today_videos": today_videos,
            "today_revenue": today_rev,
            "total_revenue": total_revenue,
            "total_videos": total_videos,
            "recent_users": recent_users,
            "recent_payments": recent_payments,
            "recent_gens": recent_gens,
            "bot_running": is_bot_running,
            "maintenance_mode": settings.is_maintenance
        }
    )


@app.post("/admin/adjust-balance")
async def adjust_balance(
    user_id: int = Form(...),
    amount: float = Form(...),
    username: str = Depends(check_admin_credentials)
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
        
        user.balance += Decimal(str(amount))
        if user.balance < 0:
            user.balance = Decimal("0.00")
            
        await session.commit()
    return RedirectResponse(url="/admin", status_code=303)


@app.get("/admin/reports/daily")
async def get_daily_report(username: str = Depends(check_admin_credentials)):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Sana", "Yangi foydalanuvchilar", "Yaratilgan videolar", 
        "Jami to'lovlar (so'm)", "Muvaffaqiyatli to'lovlar (so'm)"
    ])
    
    async with AsyncSessionLocal() as session:
        # Oxirgi 30 kun uchun hisobot
        for i in range(30):
            day = datetime.utcnow().date() - timedelta(days=i)
            start_dt = datetime.combine(day, datetime.min.time())
            end_dt = datetime.combine(day, datetime.max.time())
            
            # Yangi foydalanuvchilar
            res_u = await session.execute(
                select(func.count(User.id)).where(User.created_at.between(start_dt, end_dt))
            )
            users_count = res_u.scalar() or 0
            
            # Videolar
            res_v = await session.execute(
                select(func.count(VideoGeneration.id)).where(
                    VideoGeneration.created_at.between(start_dt, end_dt)
                )
            )
            videos_count = res_v.scalar() or 0
            
            # Jami va tasdiqlangan to'lovlar
            res_p_all = await session.execute(
                select(func.sum(Payment.amount)).where(Payment.created_at.between(start_dt, end_dt))
            )
            all_pay = res_p_all.scalar() or Decimal("0.00")
            
            res_p_conf = await session.execute(
                select(func.sum(Payment.amount)).where(
                    Payment.created_at.between(start_dt, end_dt),
                    Payment.status == "confirmed"
                )
            )
            conf_pay = res_p_conf.scalar() or Decimal("0.00")
            
            writer.writerow([day.strftime("%Y-%m-%d"), users_count, videos_count, all_pay, conf_pay])
            
    output.seek(0)
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=daily_report.csv"
    return response


@app.get("/admin/reports/monthly")
async def get_monthly_report(username: str = Depends(check_admin_credentials)):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Oy", "Yangi foydalanuvchilar", "Yaratilgan videolar", 
        "Jami to'lovlar (so'm)", "Muvaffaqiyatli to'lovlar (so'm)"
    ])
    
    async with AsyncSessionLocal() as session:
        # Oxirgi 12 oy uchun hisobot
        for i in range(12):
            today = datetime.utcnow().date()
            # Oyni hisoblash
            first_day_of_this_month = today.replace(day=1)
            target_month_first_day = (first_day_of_this_month - timedelta(days=i*30)).replace(day=1)
            
            # Kelgusi oyning boshlanishi
            if target_month_first_day.month == 12:
                next_month_first_day = target_month_first_day.replace(year=target_month_first_day.year + 1, month=1)
            else:
                next_month_first_day = target_month_first_day.replace(month=target_month_first_day.month + 1)
                
            start_dt = datetime.combine(target_month_first_day, datetime.min.time())
            end_dt = datetime.combine(next_month_first_day, datetime.min.time()) - timedelta(seconds=1)
            
            # Yangi foydalanuvchilar
            res_u = await session.execute(
                select(func.count(User.id)).where(User.created_at.between(start_dt, end_dt))
            )
            users_count = res_u.scalar() or 0
            
            # Videolar
            res_v = await session.execute(
                select(func.count(VideoGeneration.id)).where(
                    VideoGeneration.created_at.between(start_dt, end_dt)
                )
            )
            videos_count = res_v.scalar() or 0
            
            # Jami va tasdiqlangan to'lovlar
            res_p_all = await session.execute(
                select(func.sum(Payment.amount)).where(Payment.created_at.between(start_dt, end_dt))
            )
            all_pay = res_p_all.scalar() or Decimal("0.00")
            
            res_p_conf = await session.execute(
                select(func.sum(Payment.amount)).where(
                    Payment.created_at.between(start_dt, end_dt),
                    Payment.status == "confirmed"
                )
            )
            conf_pay = res_p_conf.scalar() or Decimal("0.00")
            
            writer.writerow([target_month_first_day.strftime("%Y-%m"), users_count, videos_count, all_pay, conf_pay])
            
    output.seek(0)
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=monthly_report.csv"
    return response

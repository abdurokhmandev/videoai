import logging
import secrets
import string
from decimal import Decimal
from datetime import datetime, timedelta, date
from typing import Optional, List, Tuple

from sqlalchemy import select, update, delete, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from bot.database.models import Base, User, VideoGeneration, Payment, Referral, PremiumSubscription
from bot.config import settings

logger = logging.getLogger(__name__)

# Create async engine dynamically checking for SQLite vs other databases
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
    )
else:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


from sqlalchemy import select, update, delete, func, and_, or_, desc, text

async def init_db():
    """Create all tables and auto-migrate schema"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # PostgreSQL uchun yangi ustunlarni avtomatik qo'shish (Auto-migration)
        if not settings.DATABASE_URL.startswith("sqlite"):
            # users jadvali migratsiyasi
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS tangas INTEGER DEFAULT 50"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS streak_days INTEGER DEFAULT 0"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_video_date DATE"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_premium BOOLEAN DEFAULT FALSE"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS premium_until TIMESTAMP"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_code VARCHAR(12)"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by BIGINT"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS free_used BOOLEAN DEFAULT FALSE"))
            
            # payments jadvali migratsiyasi
            await conn.execute(text("ALTER TABLE payments ADD COLUMN IF NOT EXISTS amount_tangas INTEGER DEFAULT 0"))
            await conn.execute(text("ALTER TABLE payments ADD COLUMN IF NOT EXISTS package VARCHAR"))
            await conn.execute(text("ALTER TABLE payments ADD COLUMN IF NOT EXISTS provider_tx_id VARCHAR"))
            await conn.execute(text("ALTER TABLE payments ADD COLUMN IF NOT EXISTS admin_confirmed BOOLEAN DEFAULT FALSE"))
            
            # Eski amount ustuni NOT NULL cheklovini xavfsiz olib tashlash (agar mavjud bo'lsa)
            await conn.execute(text("""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name='payments' AND column_name='amount'
                    ) THEN
                        ALTER TABLE payments ALTER COLUMN amount DROP NOT NULL;
                    END IF;
                END $$;
            """))
            
            # video_generations jadvali migratsiyasi
            await conn.execute(text("ALTER TABLE video_generations ADD COLUMN IF NOT EXISTS cost_tangas INTEGER DEFAULT 30"))
            await conn.execute(text("ALTER TABLE video_generations ADD COLUMN IF NOT EXISTS duration_sec INTEGER DEFAULT 5"))
            await conn.execute(text("ALTER TABLE video_generations ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP"))
            
            # Eski foydalanuvchilarga referral_code o'rnatish
            await conn.execute(text("UPDATE users SET referral_code = substr(md5(random()::text), 1, 8) WHERE referral_code IS NULL"))
            
    logger.info("Database tables created/verified and auto-migrated successfully.")



def generate_referral_code(length: int = 8) -> str:
    """Generate unique referral code"""
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


# ─── USER QUERIES ─────────────────────────────────────────────────────────────

async def get_or_create_user(
    session: AsyncSession,
    user_id: int,
    username: Optional[str],
    full_name: Optional[str],
) -> Tuple[User, bool]:
    """Get existing user or create new one. Returns (user, is_new)"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user:
        # Update last_active and info
        user.last_active = func.now()
        if username:
            user.username = username
        if full_name:
            user.full_name = full_name
        await session.commit()
        return user, False

    # Create new user with referral code and welcome 50 tangas
    ref_code = generate_referral_code()
    user = User(
        id=user_id,
        username=username,
        full_name=full_name,
        referral_code=ref_code,
        tangas=50,  # Boshlang'ich 50 tanga
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user, True


async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_referral_code(
    session: AsyncSession, ref_code: str
) -> Optional[User]:
    result = await session.execute(
        select(User).where(User.referral_code == ref_code)
    )
    return result.scalar_one_or_none()


async def add_tangas(
    session: AsyncSession, user_id: int, amount: int
) -> int:
    """Add tangas to user. Returns new tangas count."""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError(f"User {user_id} not found")
    user.tangas += amount
    await session.commit()
    await session.refresh(user)
    return user.tangas


async def deduct_tangas(
    session: AsyncSession, user_id: int, amount: int
) -> int:
    """Deduct tangas from user. Returns new tangas count."""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError(f"User {user_id} not found")
    if user.tangas < amount:
        raise ValueError("Insufficient tangas balance")
    user.tangas -= amount
    await session.commit()
    await session.refresh(user)
    return user.tangas


async def mark_free_used(session: AsyncSession, user_id: int):
    await session.execute(
        update(User).where(User.id == user_id).values(free_used=True)
    )
    await session.commit()


async def set_language(session: AsyncSession, user_id: int, lang: str):
    await session.execute(
        update(User).where(User.id == user_id).values(language=lang)
    )
    await session.commit()


async def block_user(session: AsyncSession, user_id: int, blocked: bool):
    await session.execute(
        update(User).where(User.id == user_id).values(is_blocked=blocked)
    )
    await session.commit()


async def get_all_users(session: AsyncSession) -> List[User]:
    result = await session.execute(select(User))
    return list(result.scalars().all())


async def get_active_users(session: AsyncSession, days: int = 30) -> List[User]:
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = await session.execute(
        select(User).where(
            and_(User.last_active >= cutoff, User.is_blocked == False)
        )
    )
    return list(result.scalars().all())


async def get_inactive_users(session: AsyncSession, days: int = 3) -> List[User]:
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = await session.execute(
        select(User).where(
            and_(User.last_active <= cutoff, User.is_blocked == False)
        )
    )
    return list(result.scalars().all())


async def get_user_count(session: AsyncSession) -> int:
    result = await session.execute(select(func.count(User.id)))
    return result.scalar_one()


async def get_new_users_today(session: AsyncSession) -> int:
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await session.execute(
        select(func.count(User.id)).where(User.created_at >= today)
    )
    return result.scalar_one()


async def get_top_users(session: AsyncSession, limit: int = 10) -> List[User]:
    result = await session.execute(
        select(User).order_by(desc(User.total_spent)).limit(limit)
    )
    return list(result.scalars().all())


async def manual_adjust_tangas(
    session: AsyncSession, user_id: int, amount: int, admin_note: str = ""
):
    """Admin: manually add or subtract tangas"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError(f"User {user_id} not found")
    user.tangas += amount
    if user.tangas < 0:
        user.tangas = 0
    await session.commit()
    return user


async def increment_streak(session: AsyncSession, user_id: int) -> int:
    """Increment user streak. Returns new streak count."""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        today_val = date.today()
        if user.last_video_date == today_val:
            # Already made a video today, streak remains same
            return user.streak_days
        elif user.last_video_date == today_val - timedelta(days=1):
            # Consecutive day!
            user.streak_days += 1
        else:
            # Streak broken, reset to 1
            user.streak_days = 1
        user.last_video_date = today_val
        await session.commit()
        return user.streak_days
    return 0


# ─── VIDEO GENERATION QUERIES ─────────────────────────────────────────────────

async def create_generation(
    session: AsyncSession,
    user_id: int,
    prompt: str,
    api_provider: str,
    cost_tangas: int = 30,
) -> VideoGeneration:
    gen = VideoGeneration(
        user_id=user_id,
        prompt=prompt,
        api_provider=api_provider,
        cost_tangas=cost_tangas,
        duration_sec=5,
        status="processing",
    )
    session.add(gen)
    await session.commit()
    await session.refresh(gen)
    return gen


async def complete_generation(
    session: AsyncSession,
    gen_id: int,
    video_url: str,
    api_job_id: Optional[str] = None,
):
    """Mark generation as done"""
    result = await session.execute(
        select(VideoGeneration).where(VideoGeneration.id == gen_id)
    )
    gen = result.scalar_one_or_none()
    if gen:
        gen.status = "done"
        gen.video_url = video_url
        gen.api_job_id = api_job_id
        gen.completed_at = func.now()
        await session.commit()


async def fail_generation(
    session: AsyncSession, gen_id: int, error_msg: str = ""
):
    result = await session.execute(
        select(VideoGeneration).where(VideoGeneration.id == gen_id)
    )
    gen = result.scalar_one_or_none()
    if gen:
        gen.status = "failed"
        gen.error_message = error_msg
        gen.completed_at = func.now()
        await session.commit()


async def update_user_stats(session: AsyncSession, user_id: int, cost_tangas: int):
    """Update total_spent and total_videos after successful generation"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.total_spent += cost_tangas
        user.total_videos += 1
        await session.commit()


async def get_user_history(
    session: AsyncSession, user_id: int, limit: int = 10, offset: int = 0
) -> List[VideoGeneration]:
    result = await session.execute(
        select(VideoGeneration)
        .where(VideoGeneration.user_id == user_id)
        .order_by(desc(VideoGeneration.created_at))
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_user_generation_count(session: AsyncSession, user_id: int) -> int:
    result = await session.execute(
        select(func.count(VideoGeneration.id)).where(
            VideoGeneration.user_id == user_id
        )
    )
    return result.scalar_one()


async def get_today_video_count(session: AsyncSession) -> int:
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await session.execute(
        select(func.count(VideoGeneration.id)).where(
            VideoGeneration.created_at >= today
        )
    )
    return result.scalar_one()


def package_price_som(package: str) -> int:
    mapping = {
        "small": 18000,
        "medium": 50000,
        "large": 120000,
        "mega": 250000
    }
    return mapping.get(package.lower(), 0)


async def get_today_revenue(session: AsyncSession) -> int:
    """Calculate today's revenue in so'm based on package pricing"""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await session.execute(
        select(Payment).where(
            and_(
                Payment.created_at >= today,
                Payment.status == "confirmed",
            )
        )
    )
    payments = result.scalars().all()
    total_revenue = 0
    for p in payments:
        total_revenue += package_price_som(p.package or "")
    return total_revenue


# ─── PAYMENT QUERIES ──────────────────────────────────────────────────────────

async def create_payment(
    session: AsyncSession,
    user_id: int,
    amount_tangas: int,
    provider: str,
    package: str,
    provider_tx_id: Optional[str] = None,
) -> Payment:
    payment = Payment(
        user_id=user_id,
        amount_tangas=amount_tangas,
        provider=provider,
        package=package,
        provider_tx_id=provider_tx_id,
        status="pending",
    )
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    return payment


async def get_payment(session: AsyncSession, payment_id: int) -> Optional[Payment]:
    result = await session.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    return result.scalar_one_or_none()


async def get_payment_by_provider_id(
    session: AsyncSession, provider_tx_id: str
) -> Optional[Payment]:
    result = await session.execute(
        select(Payment).where(Payment.provider_tx_id == provider_tx_id)
    )
    return result.scalar_one_or_none()


async def check_and_apply_referral_bonus(session: AsyncSession, referred_id: int) -> Optional[int]:
    """
    Foydalanuvchi tanga sotib olganida uni taklif qilgan do'stiga tanga berish.
    Taklif qilgan do'stining ID-sini qaytaradi (xabarnoma yuborish uchun).
    """
    result = await session.execute(
        select(Referral).where(
            and_(
                Referral.referred_id == referred_id,
                Referral.bonus_given == False
            )
        )
    )
    ref = result.scalar_one_or_none()
    if ref:
        ref.bonus_given = True
        # Faqat taklif qilgan (referrer) foydalanuvchiga bonus 20 tanga beriladi
        await add_tangas(session, ref.referrer_id, 20)
        return ref.referrer_id
    return None


async def confirm_payment(session: AsyncSession, payment_id: int) -> Tuple[Optional[Payment], Optional[int]]:
    result = await session.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    referrer_id = None
    if payment:
        payment.status = "confirmed"
        payment.confirmed_at = func.now()
        # Add tangas to the user
        await add_tangas(session, payment.user_id, payment.amount_tangas)
        
        # Referral bonusni tekshirish va berish
        referrer_id = await check_and_apply_referral_bonus(session, payment.user_id)
        
        await session.commit()
    return payment, referrer_id


async def confirm_manual_payment(session: AsyncSession, payment_id: int) -> Tuple[Optional[Payment], Optional[int]]:
    result = await session.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    referrer_id = None
    if payment:
        payment.status = "confirmed"
        payment.admin_confirmed = True
        payment.confirmed_at = func.now()
        # Add tangas to the user
        await add_tangas(session, payment.user_id, payment.amount_tangas)
        
        # Referral bonusni tekshirish va berish
        referrer_id = await check_and_apply_referral_bonus(session, payment.user_id)
        
        await session.commit()
    return payment, referrer_id


async def cancel_payment(session: AsyncSession, provider_tx_id: str):
    result = await session.execute(
        select(Payment).where(Payment.provider_tx_id == provider_tx_id)
    )
    payment = result.scalar_one_or_none()
    if payment:
        payment.status = "cancelled"
        await session.commit()
    return payment


async def get_recent_payments(
    session: AsyncSession, limit: int = 20
) -> List[Payment]:
    result = await session.execute(
        select(Payment).order_by(desc(Payment.created_at)).limit(limit)
    )
    return list(result.scalars().all())


# ─── REFERRAL QUERIES ─────────────────────────────────────────────────────────

async def create_referral(
    session: AsyncSession, referrer_id: int, referred_id: int
) -> Optional[Referral]:
    """Create referral link. Returns None if already exists."""
    try:
        ref = Referral(referrer_id=referrer_id, referred_id=referred_id)
        session.add(ref)
        await session.commit()
        await session.refresh(ref)
        return ref
    except Exception:
        await session.rollback()
        return None


async def give_referral_bonus(session: AsyncSession, referral_id: int):
    result = await session.execute(
        select(Referral).where(Referral.id == referral_id)
    )
    ref = result.scalar_one_or_none()
    if ref:
        ref.bonus_given = True
        # Award both 20 tangas
        await add_tangas(session, ref.referrer_id, 20)
        await add_tangas(session, ref.referred_id, 20)
        await session.commit()


async def get_referral_stats(session: AsyncSession, user_id: int) -> dict:
    """Get referral statistics for a user"""
    result = await session.execute(
        select(func.count(Referral.id), func.sum(
            func.cast(Referral.bonus_given, Integer)
        )).where(Referral.referrer_id == user_id)
    )
    row = result.one()
    total = row[0] or 0
    bonuses = row[1] or 0
    return {"total_referred": total, "bonuses_given": bonuses}

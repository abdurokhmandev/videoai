import base64
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.database.queries import get_or_create_user, create_payment, AsyncSessionLocal
from bot.utils.messages import get_msg
from bot.keyboards.payment import packages_keyboard, payment_method_keyboard
from bot.keyboards.main import back_button
from bot.config import settings

router = Router()


@router.message(Command("topup"))
async def topup_message_handler(message: Message):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        text = get_msg(user.language, "topup_menu").format(balance=user.balance)
        keyboard = packages_keyboard(user.language)
        keyboard.inline_keyboard.append(back_button(user.language).inline_keyboard[0])
        await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "topup")
async def topup_callback_handler(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name
        )
        
        text = get_msg(user.language, "topup_menu").format(balance=user.balance)
        keyboard = packages_keyboard(user.language)
        keyboard.inline_keyboard.append(back_button(user.language).inline_keyboard[0])
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()


@router.callback_query(F.data.startswith("pkg_"))
async def package_select_handler(callback: CallbackQuery):
    package_key = callback.data.split("_")[1]
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name
        )
        
        pkg = settings.packages.get(package_key)
        if not pkg:
            await callback.answer("Paket topilmadi!", show_alert=True)
            return
            
        text = get_msg(user.language, "select_payment").format(
            package_name=pkg["name"],
            price=pkg["price"],
            videos=pkg["videos"]
        )
        
        keyboard = payment_method_keyboard(package_key, user.language)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()


@router.callback_query(F.data.startswith("pay_"))
async def payment_process_handler(callback: CallbackQuery):
    _, provider, package_key = callback.data.split("_")
    
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name
        )
        
        pkg = settings.packages.get(package_key)
        if not pkg:
            await callback.answer("Paket topilmadi!", show_alert=True)
            return
            
        price = pkg["price"]
        
        # Bazada to'lov tranzaksiyasini yaratish
        db_payment = await create_payment(
            session=session,
            user_id=user.id,
            amount=price,
            provider=provider,
            package=package_key
        )
        
        # Dinamik to'lov havolasini yaratish
        payment_url = "#"
        if provider == "payme":
            # Payme uchun havola yaratish (Base64 encoding bilan)
            merchant_id = settings.PAYME_MERCHANT_ID or "65f123456789abcde"
            params = f"m={merchant_id};ac.order_id={db_payment.id};a={int(price * 100)}"
            encoded = base64.b64encode(params.encode()).decode()
            payment_url = f"https://checkout.payme.uz/{encoded}"
        else:
            # Click uchun havola yaratish
            service_id = settings.CLICK_SERVICE_ID or "12345"
            merchant_id = settings.CLICK_MERCHANT_ID or "54321"
            payment_url = (
                f"https://my.click.uz/services/pay"
                f"?service_id={service_id}&merchant_id={merchant_id}"
                f"&amount={price}&transaction_param={db_payment.id}"
            )
            
        text = get_msg(user.language, "payment_link").format(link=payment_url)
        keyboard = back_button(user.language)
        
        await callback.message.edit_text(text, reply_markup=keyboard, disable_web_page_preview=True)
        await callback.answer()

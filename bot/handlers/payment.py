from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import settings
from bot.utils.messages import get_msg
from bot.services.stars import get_stars_invoice
from bot.database.queries import (
    get_or_create_user, create_payment, confirm_payment,
    confirm_manual_payment, AsyncSessionLocal
)
from bot.keyboards.payment import (
    packages_keyboard, payment_methods_keyboard,
    manual_payment_confirm_keyboard
)

router = Router()


class ManualPaymentState(StatesGroup):
    waiting_for_receipt = State()


# ─── TELEGRAM STARS PAYMENTS ──────────────────────────────────────────────────

@router.callback_query(F.data.startswith("pay_stars_"))
async def pay_stars_callback(callback: CallbackQuery):
    package_key = callback.data.split("_")[2]
    pkg_data = settings.packages.get(package_key)
    
    if not pkg_data:
        await callback.answer("Paket topilmadi!", show_alert=True)
        return
        
    invoice_args = get_stars_invoice(package_key, pkg_data)
    await callback.message.delete()
    
    # Telegram Stars Invoice yuborish
    await callback.message.answer_invoice(
        title=invoice_args["title"],
        description=invoice_args["description"],
        payload=invoice_args["payload"],
        provider_token=invoice_args["provider_token"],
        currency=invoice_args["currency"],
        prices=invoice_args["prices"]
    )
    await callback.answer()


@router.pre_checkout_query()
async def stars_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    """Stars to'lovidan oldingi tekshiruv"""
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def stars_successful_payment(message: Message):
    """Muvaffaqiyatli Stars to'lovi qabul qilinganda"""
    payload = message.successful_payment.invoice_payload
    package_key = payload.replace("stars_pkg_", "")
    
    pkg_data = settings.packages.get(package_key)
    if not pkg_data:
        await message.answer("⚠️ Paket xatoligi! Admin bilan bog'laning.")
        return
        
    async with AsyncSessionLocal() as session:
        # To'lovni bazaga yozish va tasdiqlash (avtomatik ravishda tangalarni qo'shadi)
        payment = await create_payment(
            session=session,
            user_id=message.from_user.id,
            amount_tangas=pkg_data["tangas"],
            provider="stars",
            package=package_key,
            provider_tx_id=message.successful_payment.telegram_payment_charge_id
        )
        payment, referrer_id = await confirm_payment(session, payment.id)
        
        if referrer_id:
            try:
                friend_name = message.from_user.full_name or "Do'stingiz"
                ref_text = (
                    "🎁 <b>Do'stingiz tanga sotib oldi!</b>\n\n"
                    f"{friend_name} taklif havolangiz orqali kirib, tanga sotib oldi.\n"
                    "Sizga <b>+20 🪙 bonus tanga</b> taqdim etildi!"
                )
                await message.bot.send_message(chat_id=referrer_id, text=ref_text)
            except Exception:
                pass
                
        user, _ = await get_or_create_user(session, message.from_user.id, None, None)
        
        text = (
            "✅ <b>To'lov muvaffaqiyatli qabul qilindi!</b>\n\n"
            f"🪙 <b>+{pkg_data['tangas']} tanga</b> hisobingizga qo'shildi!\n"
            f"💳 Joriy tangalaringiz: <b>{user.tangas} ta</b>\n\n"
            "🎬 Video yaratishni boshlashingiz mumkin! 🚀"
        )
        await message.answer(text)


# ─── MANUAL KARTA PAYMENTS (QO'LDA) ───────────────────────────────────────────

@router.callback_query(F.data.startswith("pay_manual_"))
async def pay_manual_callback(callback: CallbackQuery):
    package_key = callback.data.split("_")[2]
    pkg_data = settings.packages.get(package_key)
    
    if not pkg_data:
        await callback.answer("Paket topilmadi!", show_alert=True)
        return
        
    text = get_msg("uz", "manual_payment").format(
        tangas=pkg_data["tangas"],
        som=pkg_data["som"],
        card_number=settings.CARD_NUMBER,
        card_owner=settings.CARD_OWNER
    )
    
    await callback.message.edit_text(
        text=text,
        reply_markup=manual_payment_confirm_keyboard(package_key)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_receipt_"))
async def confirm_receipt_callback(callback: CallbackQuery, state: FSMContext):
    package_key = callback.data.split("_")[2]
    await state.update_data(package_key=package_key)
    
    await callback.message.edit_text(
        "📸 <b>Iltimos, amalga oshirilgan to'lov chekini (rasmini) yuboring:</b>\n\n"
        "Chek rasmini yuborganingizdan so'ng adminlarimiz uni tekshirib, 5-30 daqiqa ichida hisobingizga tangalarni taqdim etishadi."
    )
    await state.set_state(ManualPaymentState.waiting_for_receipt)
    await callback.answer()


@router.message(ManualPaymentState.waiting_for_receipt, F.photo)
async def receipt_photo_handler(message: Message, state: FSMContext, bot: Bot):
    photo = message.photo[-1]
    data = await state.get_data()
    package_key = data.get("package_key", "medium")
    
    pkg_data = settings.packages.get(package_key)
    if not pkg_data:
        await message.answer("Xatolik yuz berdi. Iltimos, bosh menyuga qaytib qaytadan urinib ko'ring.")
        await state.clear()
        return
        
    async with AsyncSessionLocal() as session:
        # To'lov ob'ektini bazada pending holatda yaratamiz
        payment = await create_payment(
            session=session,
            user_id=message.from_user.id,
            amount_tangas=pkg_data["tangas"],
            provider="manual",
            package=package_key,
            provider_tx_id=photo.file_id  # Chek rasmining file_id sini saqlaymiz
        )
        
        await state.clear()
        
        await message.answer(
            "✅ <b>Chek qabul qilindi!</b>\n\n"
            "Adminlarimiz uni tez fursatda tekshirishadi va tangalar hisobingizga qo'shiladi. Rahmat!"
        )
        
        # Barcha adminlarga chek va tasdiqlash inline tugmalarini yuborish
        for admin_id in settings.admin_ids_list:
            try:
                admin_text = (
                    "💳 <b>YANGI TO'LOV CHEKI (QO'LDA)</b>\n\n"
                    f"👤 <b>Foydalanuvchi:</b> {message.from_user.full_name} (@{message.from_user.username or 'yoq'}, ID: <code>{message.from_user.id}</code>)\n"
                    f"📦 <b>Paket:</b> {pkg_data['name']} ({pkg_data['tangas']} tanga)\n"
                    f"💰 <b>Narxi:</b> {pkg_data['som']:,} so'm\n"
                    f"🆔 <b>To'lov ID:</b> {payment.id}\n"
                    "━━━━━━━━━━━━━━━━━━━━"
                )
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"admin_confirm_pay_{payment.id}"),
                        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"admin_reject_pay_{payment.id}")
                    ]
                ])
                await bot.send_photo(
                    chat_id=admin_id,
                    photo=photo.file_id,
                    caption=admin_text,
                    reply_markup=kb
                )
            except Exception as e:
                pass


@router.message(ManualPaymentState.waiting_for_receipt)
async def receipt_not_photo_handler(message: Message):
    await message.answer("⚠️ Iltimos, to'lov chekini faqat <b>rasm (photo)</b> ko'rinishida yuboring.")

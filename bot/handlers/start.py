from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from bot.config import settings
from bot.utils.messages import get_msg
from bot.database.queries import (
    get_or_create_user, add_balance, mark_free_used, 
    AsyncSessionLocal, set_language
)
from bot.keyboards.main import main_keyboard, settings_keyboard, language_select_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    async with AsyncSessionLocal() as session:
        user, is_new = await get_or_create_user(
            session=session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        # Agarda yangi foydalanuvchi bo'lsa va hali bepul bonus olmagan bo'lsa
        if not user.free_used:
            await add_balance(session, user.id, settings.FREE_VIDEO_VALUE_SOM)
            await mark_free_used(session, user.id)
            
            # Yangi foydalanuvchiga til tanlash tugmalarini chiqarish (Orqaga tugmasiz)
            text = (
                "🇺🇿 <b>Salom! Loyihamizga xush kelibsiz!</b>\n"
                "Iltimos, muloqot tilini tanlang 👇\n\n"
                "🇷🇺 <b>Привет! Добро пожаловать!</b>\n"
                "Пожалуйста, выберите язык общения 👇"
            )
            await message.answer(text, reply_markup=language_select_keyboard())
        else:
            # Mavjud foydalanuvchiga to'g'ridan-to'g'ri chiroyli Bosh Menyuni chiqarish
            text = get_msg(user.language, "start_existing")
            await message.answer(text, reply_markup=main_keyboard(user.language))


@router.callback_query(F.data.startswith("set_lang_"))
async def set_lang_callback(callback: CallbackQuery):
    lang = callback.data.split("_")[2]
    async with AsyncSessionLocal() as session:
        await set_language(session, callback.from_user.id, lang)
        
        # Til muvaffaqiyatli saqlangach, tabriklash xabari va menyuni chiqarish
        welcome_text = get_msg(lang, "start") + f"\n\n🎁 <b>Sizga 1 ta bepul video sovg'a qilindi ({settings.FREE_VIDEO_VALUE_SOM:,} so'm)!</b>"
        await callback.message.edit_text(welcome_text, reply_markup=main_keyboard(lang))
        await callback.answer("Til sozlandi! / Язык настроен!")


@router.callback_query(F.data == "back_main")
async def back_main_callback(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name
        )
        text = get_msg(user.language, "start_existing")
        await callback.message.edit_text(text, reply_markup=main_keyboard(user.language))
        await callback.answer()

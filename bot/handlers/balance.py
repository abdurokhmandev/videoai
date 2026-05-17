from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.database.queries import (
    get_or_create_user, get_user_history, get_user_generation_count, AsyncSessionLocal
)
from bot.utils.messages import get_msg
from bot.keyboards.main import balance_keyboard, history_keyboard, back_button
from bot.utils.helpers import truncate_text, status_emoji, model_emoji

router = Router()


@router.message(Command("balance"))
async def balance_message_handler(message: Message):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        status_name = "Premium User 🏆" if user.total_spent > 0 else "Oddiy Foydalanuvchi"
        text = get_msg(user.language, "balance_info").format(
            balance=user.balance,
            total_videos=user.total_videos,
            total_spent=user.total_spent,
            created=user.created_at.strftime("%Y-%m-%d"),
            status=status_name
        )
        
        keyboard = balance_keyboard(user.language)
        keyboard.inline_keyboard.append(back_button(user.language).inline_keyboard[0])
        await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "balance")
async def balance_callback_handler(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user, _ = await get_or_create_user(
            session=session,
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name
        )
        
        status_name = "Premium User 🏆" if user.total_spent > 0 else "Oddiy Foydalanuvchi"
        text = get_msg(user.language, "balance_info").format(
            balance=user.balance,
            total_videos=user.total_videos,
            total_spent=user.total_spent,
            created=user.created_at.strftime("%Y-%m-%d"),
            status=status_name
        )
        
        keyboard = balance_keyboard(user.language)
        keyboard.inline_keyboard.append(back_button(user.language).inline_keyboard[0])
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()


@router.message(Command("history"))
async def history_message_handler(message: Message):
    await show_history(message, message.from_user.id, offset=0, is_callback=False)


@router.callback_query(F.data.startswith("history_"))
async def history_callback_handler(callback: CallbackQuery):
    offset = int(callback.data.split("_")[1])
    await show_history(callback.message, callback.from_user.id, offset=offset, is_callback=True)
    await callback.answer()


async def show_history(message_obj, user_id: int, offset: int = 0, is_callback: bool = False):
    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(
            session=session,
            user_id=user_id,
            username=None,
            full_name=None
        )
        user_lang = user[0].language
        
        # Tarixni bazadan yuklash (har bir sahifada 5 tadan ko'rsatamiz)
        history_list = await get_user_history(session, user_id, limit=5, offset=offset)
        total_count = await get_user_generation_count(session, user_id)
        
        if not history_list:
            text = get_msg(user_lang, "history_empty")
            keyboard = back_button(user_lang)
            if is_callback:
                await message_obj.edit_text(text, reply_markup=keyboard)
            else:
                await message_obj.answer(text, reply_markup=keyboard)
            return
            
        text = get_msg(user_lang, "history_header") + "\n"
        for i, item in enumerate(history_list, start=offset + 1):
            date_str = item.created_at.strftime("%d.%m %H:%M")
            prompt_truncated = truncate_text(item.prompt, max_len=40)
            emoji = status_emoji(item.status)
            model_info = model_emoji(item.api_provider)
            
            text += get_msg(user_lang, "history_item").format(
                num=i,
                date=date_str,
                prompt=prompt_truncated,
                model=model_info,
                status=emoji,
                cost=item.cost_som
            ) + "\n"
            
        # Sahifalangan inline tugmalarini yaratish
        keyboard = history_keyboard(offset, total_count, user_lang)
        keyboard.inline_keyboard.append(back_button(user_lang).inline_keyboard[0])
        
        if is_callback:
            await message_obj.edit_text(text, reply_markup=keyboard)
        else:
            await message_obj.answer(text, reply_markup=keyboard)

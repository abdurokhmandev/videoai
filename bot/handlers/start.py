from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.utils.messages import get_msg
from bot.database.queries import get_or_create_user, add_balance, mark_free_used, AsyncSessionLocal
from bot.config import settings

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
        if not user.free_used:
            await add_balance(session, user.id, settings.FREE_VIDEO_VALUE_SOM)
            await mark_free_used(session, user.id)
            await message.answer(get_msg(user.language, "start") + "\n\n🎁 Sizga 1 bepul video berildi!")
        else:
            await message.answer(get_msg(user.language, "start"))

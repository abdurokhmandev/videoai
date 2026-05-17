from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from bot.config import settings


class MaintenanceMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            if settings.is_maintenance:
                await event.answer("Botda texnik ishlar olib borilmoqda")
                return  # Boshqa handlerlar ishlamasligi uchun bu yerda to'xtatamiz
        
        return await handler(event, data)

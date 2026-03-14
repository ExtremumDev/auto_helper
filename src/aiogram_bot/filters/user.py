from aiogram.filters import BaseFilter

from src.aiogram_bot.config import ADMINS


class AdminFilter(BaseFilter):

    async def __call__(self, telegram_obj, *args, **kwargs):
        return telegram_obj.from_user.id in ADMINS

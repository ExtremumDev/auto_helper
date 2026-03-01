from aiogram.filters import BaseFilter

from src.aiogram_bot.database.utils import provide_user
from src.aiogram_bot.services.data.context import ServiceContext
from src.common.databsae.models.user import User


class AdminFilter(BaseFilter):

    @provide_user
    async def __call__(self, user: User, *args, **kwargs):
        if user:
            return user.is_admin
        else:
            return False

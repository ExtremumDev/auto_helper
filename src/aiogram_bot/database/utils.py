import functools

from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.databsae.core.database import connection
from src.common.databsae.dao.user import UserDAO


@connection
def provide_user(func):
    async def wrapper(db_session: AsyncSession, *args, **kwargs):
        if args:
            telegram_obj = args[0]

            if not isinstance(telegram_obj, TelegramObject):
                raise ValueError("Provide user database decorator: could be used only for aiogram's handlers")
        else:
            raise ValueError("Provide user database decorator: could be used only for aiogram's handlers")

        user = await UserDAO.get_obj(session=db_session, telegram_user_id=telegram_obj.from_user.id)

        await func(*args, **kwargs, db_session=db_session, user=user)
    return wrapper

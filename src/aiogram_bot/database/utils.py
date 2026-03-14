import functools

from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database.core.database import connection
from src.common.database.dao.user import UserDAO


def provide_user(load_tg_account: bool = False):
    def decorator(func):
        @connection
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if args:
                telegram_obj = args[0]

                if not isinstance(telegram_obj, TelegramObject):
                    raise ValueError("Provide user database decorator: could be used only for aiogram's handlers")
            else:
                raise ValueError("Provide user database decorator: could be used only for aiogram's handlers")

            db_session = kwargs.get('db_session')
            if not db_session:
                for arg in args:
                    if isinstance(arg, AsyncSession):
                        kwargs["db_session"] = arg
                        break
            user = await UserDAO.get_obj(
                session=db_session,
                load_tg_account=load_tg_account,
                telegram_user_id=telegram_obj.from_user.id
            )

            await func(*args, **kwargs, user=user)
        return wrapper
    return decorator

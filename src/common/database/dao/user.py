from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.common.database.dao.base import BaseDAO
from src.common.database.models.user import User, TelegramAccount


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def get_obj(cls, session: AsyncSession, load_tg_account: bool=False, **values):
        query = select(cls.model).filter_by(**values)

        if load_tg_account:
            query = query.options(
                joinedload(User.telegram_account)
            )

        result = await session.execute(query)
        obj = result.scalar_one_or_none()
        return obj


class TelegramAccountDAO(BaseDAO):

    model = TelegramAccount

    @classmethod
    async def get_active_accounts(cls, db_session: AsyncSession) -> Iterable[TelegramAccount]:
        return await cls.get_many(
            session=db_session,

        )

    @classmethod
    async def get_account_by_phone(cls, db_session: AsyncSession, phone: str) -> TelegramAccount | None:
        return await cls.get_obj(session=db_session, phone_number=phone)

    @classmethod
    async def get_account_with_user(cls, db_session: AsyncSession, **filters) -> TelegramAccount | None:
        query = select(TelegramAccount).filter_by(
            **filters
        ).options(
            joinedload(TelegramAccount.user)
        )

        res = await db_session.execute(query)

        return res.scalar_one_or_none()

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.databsae.dao.user import UserDAO


class UserService:

    async def register_user(self, telegram_user_id: int, db_session: AsyncSession):
        await UserDAO.add(
            session=db_session,
            telegram_user_id=telegram_user_id,
            is_admin=False
        )


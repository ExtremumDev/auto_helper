
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from src.aiogram_bot.utils.paging.base import Paging
from src.common.database.dao.user import UserDAO
from src.common.database.models.user import User


class UsersPaging(Paging):
    prefix = "u"

    def __init__(self, page: int = 0):
        super().__init__(page=page, prefix=self.prefix)

    async def get_queryset(self, db_session: AsyncSession, *args, **kwargs):
        self.queryset = await UserDAO.get_many(session=db_session)
        self._compute_total_pages()

    def get_reply_markup(self, *args, **kwargs):
        buttons = []

        u: User
        for u in self.queryset:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=u.telegram_username if u.telegram_username else str(u.telegram_user_id),
                        callback_data=f"user_{u.id}"
                    )
                ]
            )

        return super().get_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=buttons
            )
        )


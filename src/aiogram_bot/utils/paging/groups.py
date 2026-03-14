from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from src.aiogram_bot.database.utils import provide_user
from src.aiogram_bot.utils.paging.base import Paging
from src.common.database.models.user import User, Group


class GroupListPaging(Paging):
    objects_on_page = 7
    EMPTY_SET_MESSAGE = "Не найдено групп"
    prefix = "g"

    def __init__(self, page: int = 0):
        super().__init__(page=page, prefix=self.prefix)


    async def get_queryset(self, user: User, *args, **kwargs):
        self.queryset = user.handling_groups
        self._compute_total_pages()

    def get_reply_markup(self, *args, **kwargs):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➕ Добавить группу", callback_data="add_group")]
            ]
        )

        g: Group
        for g in self.queryset:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(text=g.display_name, callback_data=" "),
                    InlineKeyboardButton(text="❌", callback_data=f"delgroup_{g.id}")
                ]
            )

        return super().get_reply_markup(reply_markup=keyboard)


    @classmethod
    @provide_user(load_groups=True)
    async def next_page_handler(cls, c: types.CallbackQuery, user: User, *args):
        c_data = c.data.split('_')

        page = int(c_data[1])

        paging = cls(page)
        await paging.get_queryset(user=user)
        await paging.create_next_page()

        await c.message.edit_reply_markup(
            reply_markup=paging.get_reply_markup()
        )

    @classmethod
    @provide_user(load_groups=True)
    async def prev_page_handler(cls, c: types.CallbackQuery, user: User, *args):
        c_data = c.data.split('_')

        page = int(c_data[1])

        paging = cls(page)
        await paging.get_queryset(user=user)
        await paging.create_prev_page()

        await c.message.edit_reply_markup(
            reply_markup=paging.get_reply_markup()
        )

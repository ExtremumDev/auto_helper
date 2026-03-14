from aiogram import types, Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.aiogram_bot.database.utils import provide_user
from src.aiogram_bot.filters.user import AdminFilter
from src.aiogram_bot.keyboards.admin import main_admin_markup
from src.aiogram_bot.keyboards.user.main import main_admin_reply_markup
from src.aiogram_bot.services.data.user import UserService
from src.common.database.models.user import User


@provide_user()
async def on_start_cmd(m: types.Message, state: FSMContext, user: User, db_session: AsyncSession, *args, **kwargs):
    await state.clear()
    if not user:
        await UserService.get_instance().register_user(
            telegram_user_id=m.from_user.id,
            telegram_username=m.from_user.username,
            db_session=db_session,
            is_admin=True
        )
    await m.answer(
        "Добро пожаловать!",
        reply_markup=main_admin_reply_markup
    )


async def open_admin_menu(m: types.Message):
    await m.answer(
        "Админ-панель",
        reply_markup=main_admin_markup
    )



def register_main_admin_handlers(dp: Dispatcher):
    dp.message.register(on_start_cmd, CommandStart(), AdminFilter(), StateFilter('*'))
    dp.message.register(open_admin_menu, F.text == "Админ-панель", AdminFilter(), StateFilter('*'))

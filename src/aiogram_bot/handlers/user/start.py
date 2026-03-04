from aiogram import Dispatcher, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.aiogram_bot.keyboards.user.tg_auth import authorization_types_markup
from src.common.database.models.user import User
from src.aiogram_bot.database.utils import provide_user
from src.aiogram_bot.services.context import ServiceContext


@provide_user
async def on_start_cmd(
        m: types.Message, state: FSMContext, user: User, db_session: AsyncSession, *args, **kwargs
):
    if user:
        await m.answer(
            "Открыто главное меню"
        )
    else:
        await ServiceContext.get_user_service().register_user(telegram_user_id=m.from_user.id, db_session=db_session)

        await m.answer(
            f"""
👋 Добро пожаловать, {m.from_user.first_name}!

🎁 Вам предоставлен тестовый период — 1 день!
📅 Действует до: 22.02.2026 10:49

Для начала работы нужно авторизовать ваш Telegram аккаунт.
Это позволит боту отслеживать сообщения в ваших группах.

Выберите способ авторизации:
""",
            reply_markup=authorization_types_markup
        )

async def cancel_action(c: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await c.answer("Действие отменено")



def register_start_handlers(dp: Dispatcher):
    dp.message.register(on_start_cmd, CommandStart(), StateFilter('*'))

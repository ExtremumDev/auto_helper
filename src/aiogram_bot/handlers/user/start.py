from aiogram import Dispatcher, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.aiogram_bot.keyboards.user.main import main_user_reply_markup
from src.aiogram_bot.keyboards.user.tg_auth import authorization_types_markup
from src.aiogram_bot.services.data.user import UserService
from src.common.database.models.user import User
from src.aiogram_bot.database.utils import provide_user


@provide_user()
async def on_start_cmd(
        m: types.Message, state: FSMContext, user: User, db_session: AsyncSession, *args, **kwargs
):
    if user:
        await m.answer(
            "Открыто главное меню",
            reply_markup=main_user_reply_markup
        )
    else:
        new_user = await UserService().get_instance().register_user(
            telegram_user_id=m.from_user.id,
            db_session=db_session,
            telegram_username=m.from_user.username
        )

        await m.answer(
            f"""
👋 Добро пожаловать, {m.from_user.first_name}!

🎁 Вам предоставлен тестовый период — 10 дней!
📅 Действует до: {new_user.expiration_date.strftime('%d-%m-%y %H:%M')}
""",
            reply_markup=main_user_reply_markup
        )

        await m.answer(
            text="""
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

import ctypes

from aiogram import Dispatcher, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.aiogram_bot.database.utils import provide_user
from src.aiogram_bot.fsm.user.tg_account import AccountAuthorizationFSM
from src.aiogram_bot.keyboards.user.tg_auth import get_input_code_markup, authorization_types_markup
from src.aiogram_bot.services.app_messaging import PyrogramAppProcedureCall
from src.aiogram_bot.services.data.tg_auth import TelegramAuthManager
from src.common.database.models.enums import TelegramAccountStatus
from src.common.database.models.user import User, TelegramAccount
from src.common.utils.auth import AuthResponseStatus
from src.common.database.dao.user import TelegramAccountDAO


@provide_user(load_tg_account=True)
async def send_auth_types(c: types.CallbackQuery, user: User, db_session: AsyncSession, *args):
    if user.telegram_account:
        if user.telegram_account.status != TelegramAccountStatus.AUTH_NEEDED:
            await c.answer("У вас уже есть авторизированный телеграмм аккаунт", show_alert=True)
            return

    await c.message.answer(
        "Выберите способ авторизации",
        reply_markup=authorization_types_markup
    )


async def start_phone_authorization(c: types.CallbackQuery, state: FSMContext):
    await state.set_state(AccountAuthorizationFSM.phone_number_sate)
    await c.message.answer(
        """Введите номер телефона, привязанный к вашему телеграмм аккаунту, в международном формате
Например: +79001234567"""
    )

    await c.answer()


@provide_user(load_tg_account=True)
async def handle_phone_number(m: types.Message, state: FSMContext, user: User, db_session: AsyncSession, *args):
    phone_number = m.text.strip() # validation
    await state.clear()

    send_code_session = await TelegramAuthManager().get_instance().start_code_authentication(
        phone_number=phone_number,
        user=user,
        db_session=db_session
    )

    await m.answer(
        text=send_code_session["text"],
        reply_markup=send_code_session["markup"]
    )


async def digit_input(c: types.CallbackQuery):

    code = c.data.split('_')[1]

    await c.message.edit_reply_markup(
        reply_markup=get_input_code_markup(code)
    )

    await c.answer()


async def erase_digit(c: types.CallbackQuery):

    data = c.data.split('_')

    if len(data) > 1:
        code = data[1]

        await c.message.edit_reply_markup(
            reply_markup=get_input_code_markup(code[: len(code) - 1])
        )

    await c.answer()


@provide_user(load_tg_account=True)
async def complete_code(c: types.CallbackQuery, user: User, state: FSMContext, db_session: AsyncSession, *args):
    data = c.data.split('_')


    if len(data) > 1:
        code = data[1]

        code_confirm_result = await PyrogramAppProcedureCall().get_instance().send_code_to_authorize(
            code=code,
            tg_account_id=user.telegram_account.id
        )

        match code_confirm_result.status:
            case AuthResponseStatus.SUCCESS:
                await c.message.answer(
                    "В аккаунт успешно произведён вход!"
                )
            case AuthResponseStatus.INVALID_CODE:
                await c.message.answer(
                    text="Неверный код, попробуйте ещё раз",
                    reply_markup=get_input_code_markup()
                )
            case AuthResponseStatus.WAITING_PASSWORD:
                await state.set_state(AccountAuthorizationFSM.password_state)
                await c.message.answer(
                    "Требуется двухфакторная аутентификация, введите пароль от аккаунта"
                )
            case AuthResponseStatus.EXPIRED:
                await c.message.answer(
                    "Срок действия кода истёк. Отправить ещё раз👇"
                )
            case AuthResponseStatus.UNEXPECTED_ERROR:
                await c.message.answer(
                    "Произошла неизвестная ошибка, повторите попытку позже или обратитесь к администратору"
                )

    else:
        await c.answer("Вы не ввели код!")


@provide_user(load_tg_account=True)
async def handle_password(m: types.Message, state: FSMContext, user: User, db_session: AsyncSession, *args):
    password = m.text

    if password:
        await state.clear()

        set_password_result = await PyrogramAppProcedureCall().get_instance().send_password_to_authorize(
            password=password,
            tg_account_id=user.telegram_account.id
        )

        match set_password_result.status:
            case AuthResponseStatus.SUCCESS:
                await m.answer(
                    "В аккаунт успешно произведён вход!"
                )
            case AuthResponseStatus.INVALID_PASSWORD:
                await m.answer(
                    text="Неверный пароль, попробуйте ещё раз"
                )
            case AuthResponseStatus.UNEXPECTED_ERROR:
                await m.answer(
                    "Произошла неизвестная ошибка, повторите попытку позже или обратитесь к администратору"
                )
    else:
        await m.answer("Введите пароль")


def register_authorization_handlers(dp: Dispatcher):
    dp.callback_query.register(send_auth_types, F.data == "authorize")
    dp.callback_query.register(start_phone_authorization, F.data == "auth_phone")
    dp.message.register(handle_phone_number, StateFilter(AccountAuthorizationFSM.phone_number_sate))
    dp.callback_query.register(digit_input, F.data.startswith("code_"))
    dp.callback_query.register(erase_digit, F.data.startswith("codeerase_"))
    dp.callback_query.register(complete_code, F.data.startswith("completecode_"))
    dp.message.register(handle_password, StateFilter(AccountAuthorizationFSM.password_state))

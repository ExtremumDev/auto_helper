import ctypes

from aiogram import Dispatcher, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.aiogram_bot.database.utils import provide_user
from src.aiogram_bot.fsm.user.tg_account import AccountAuthorizationFSM
from src.aiogram_bot.keyboards.user.tg_auth import get_input_code_markup
from src.aiogram_bot.services.app_messaging import PyrogramAppProcedureCall
from src.aiogram_bot.services.context import ServiceContext
from src.common.database.models.user import User, TelegramAccount
from src.common.utils.auth import AuthResponseStatus
from src.common.database.dao.user import TelegramAccountDAO


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

    auth_response = await ServiceContext.get_app_messaging_service().create_authorize_task(
        phone_number=phone_number
    )

    match auth_response.status:
        case AuthResponseStatus.WAITING_CODE:
            if auth_response.tg_account_id:
                tg_account = await TelegramAccountDAO.get_account_with_user(
                    db_session=db_session, id=auth_response.tg_account_id
                )

                if tg_account and not ServiceContext.get_telegram_auth_manager().check_owner_availabiltiy(
                        user=user,
                        tg_account=tg_account
                ):
                    await m.answer(
                        "Аккаунт с этим номером используется другим пользователем"
                    )
                    return
                if tg_account:
                    user.telegram_account = tg_account
                    await db_session.commit()

                    await m.answer(
                        "Введите код подтверждения",
                        reply_markup=get_input_code_markup()
                    )
                else:
                    await m.answer(
                        "Произошла неизвестная ошибка, попробуйте ещё раз"
                    )
            else:
                await m.answer(
                    "Произошла неизвестная ошибка, попробуйте ещё раз"
                )
        case AuthResponseStatus.INVALID_PHONE:
            await m.answer(
                "Введён неверный номер телефона, не связанный с действующим аккаунтом. Попробуйте еще раз"
            )
        case AuthResponseStatus.FLOOD_WAIT:
            await m.answer(
                "Слишком много попыток! Попробуйте позже"
            )
        case AuthResponseStatus.UNEXPECTED_ERROR:
            await m.answer(
                "Произошла неизвестная ошибка, попробуйте позже или обратитесь к администратору"
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

        code_confirm_result = await ServiceContext.get_app_messaging_service().send_code_to_authorize(
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

        set_password_result = await ServiceContext.get_app_messaging_service().send_password_to_authorize(
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
    dp.callback_query.register(start_phone_authorization, F.data == "auth_phone")
    dp.message.register(handle_phone_number, StateFilter(AccountAuthorizationFSM.phone_number_sate))
    dp.callback_query.register(digit_input, F.data.startswith("code_"))
    dp.callback_query.register(erase_digit, F.data.startswith("codeerase_"))
    dp.callback_query.register(complete_code, F.data.startswith("completecode_"))
    dp.message.register(handle_password, StateFilter(AccountAuthorizationFSM.password_state))

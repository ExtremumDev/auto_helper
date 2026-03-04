import ctypes

from aiogram import Dispatcher, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from src.aiogram_bot.fsm.user.tg_account import AccountAuthorizationFSM
from src.aiogram_bot.keyboards.user.tg_auth import get_input_code_markup
from src.aiogram_bot.services.context import ServiceContext


async def start_phone_authorization(c: types.CallbackQuery, state: FSMContext):
    await state.set_state(AccountAuthorizationFSM.phone_number_sate)
    await c.message.answer(
        """Введите номер телефона, привязанный к вашему телеграмм аккаунту, в международном формате
Например: +79001234567"""
    )

    await c.answer()


async def handle_phone_number(m: types.Message, state: FSMContext):
    phone_number = m.text.strip() # validation
    await state.clear()

    # await ServiceContext.get_app_messaging_service().create_authorize_task()

    await m.answer(
        "Введите код",
        reply_markup=get_input_code_markup()
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


async def complete_code(c: types.CallbackQuery):
    data = c.data.split('_')


    if len(data) > 1:
        code = data[1]

    else:
        await c.answer("Вы не ввели код!")


def register_authorization_handlers(dp: Dispatcher):
    dp.callback_query.register(start_phone_authorization, F.data == "auth_phone")
    dp.message.register(handle_phone_number, StateFilter(AccountAuthorizationFSM.phone_number_sate))
    dp.callback_query.register(digit_input, F.data.startswith("code_"))
    dp.callback_query.register(erase_digit, F.data.startswith("codeerase_"))
    dp.callback_query.register(complete_code, F.data.startswith("completecode_"))

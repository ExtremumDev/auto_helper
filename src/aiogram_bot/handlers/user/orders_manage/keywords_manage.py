from aiogram import types, F, Dispatcher
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.aiogram_bot.database.utils import provide_user
from src.aiogram_bot.fsm.user.orders_manage import KeywordsInputFSM
from src.aiogram_bot.keyboards.user.main import cancel_inline_markup
from src.aiogram_bot.keyboards.user.orders_manage import get_main_order_manage_markup
from src.aiogram_bot.services.data.user import UserService
from src.aiogram_bot.utils.exceptions import ValidationError
from src.aiogram_bot.utils.text import get_orders_settings_descr
from src.common.database.models.user import User


@provide_user
async def send_info(m: types.Message, db_session: AsyncSession, user: User, *args):

    await m.answer(
        text=get_orders_settings_descr(user.order_keywords, user.except_words),
        reply_markup=get_main_order_manage_markup()
    )


async def ask_keywords(c: types.CallbackQuery, state: FSMContext):
    edit = c.data.split('_')[1]

    await state.set_state(KeywordsInputFSM.words_state)
    await state.update_data(edit=edit)

    message_text = ""
    if edit == "keywords":
        message_text = "Введите список ключевых слов для поиска заказов. "
    elif edit == "exceptions":
        message_text = "Введите список слов-исключений для поиска заказов. "

    await c.message.answer(
        message_text + "Указывайте слова через запятую",
        reply_markup=cancel_inline_markup
    )

    await c.answer()


@provide_user
async def handle_new_keywords(
        m: types.Message, state: FSMContext, db_session: AsyncSession, user: User, *args
):
    data = m.text.strip()

    s_data = await state.get_data()
    await state.clear()
    edit = s_data["edit"]

    try:
        await UserService.get_instance().update_keywords(data, user=user, db_session=db_session, editing=edit)

        await m.answer(
            "Список успешно обновлён!"
        )
    except ValidationError as e:
        await m.answer(
            "Произошла ошибка: " + e.get_message() + "\nПопробуйте ввести ещё раз",
            reply_markup=cancel_inline_markup
        )



def register_keywords_manage_handlers(dp: Dispatcher):
    dp.message.register(send_info, F.text == "Настройка фильтрации заказов")

    dp.callback_query.register(ask_keywords, F.data.startswith("editw_"))
    dp.message.register(handle_new_keywords, StateFilter(KeywordsInputFSM.words_state))


import datetime

from aiogram import types, Dispatcher, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.aiogram_bot.filters.user import AdminFilter
from src.aiogram_bot.fsm.admin.users_manage import ChangeUserTariffFSM
from src.aiogram_bot.keyboards.admin.users_manage import get_users_manage_markup, get_change_tariff_markup, \
    tariff_date_markup
from src.aiogram_bot.services.data.tg_auth import TelegramAuthManager
from src.aiogram_bot.services.data.user import UserService
from src.aiogram_bot.utils.paging.user import UsersPaging
from src.aiogram_bot.utils.text import get_subscription_info_text
from src.common.database.core.database import connection
from src.common.database.dao.user import UserDAO
from src.common.database.models.enums import SubscribeTariffEnum


@connection
async def send_users_list(c: types.CallbackQuery, db_session: AsyncSession, *args):
    paging = UsersPaging()
    await paging.get_queryset(db_session=db_session)
    await paging.get_current_page()

    await c.message.answer(
        text="Выберите пользователя",
        reply_markup=paging.get_reply_markup()
    )

    await c.answer()


@connection
async def send_user_card(c: types.CallbackQuery, db_session: AsyncSession, *args):
    user_id = int(c.data.split('_')[1])
    user = await UserDAO.get_obj(session=db_session, load_tg_account=True, id=user_id)

    if user:
        reg_date = "Дата регистрации: " + user.register_date

        if user.telegram_account:
            account_text = "🟢 Телеграмм аккаунт привязан"
        else:
            account_text = "🔴 Телеграмм аккаунт не привязан"

        sub_info = get_subscription_info_text(is_subscribed=user.is_subscribed, tariff=user.sub_tariff, expire_date=user.expiration_date)

        await c.message.answer(
            reg_date + "\n" + account_text + "\n\n" + sub_info,
            reply_markup=get_users_manage_markup(user_id=user_id)
        )
        await c.answer()
    else:
        await c.answer("Пользователь не найден")


@connection
async def ask_changing_tariff(c: types.CallbackQuery, db_session: AsyncSession, *args):
    user_id = int(c.data.split('_')[1])
    user = await UserDAO.get_obj(session=db_session, load_tg_account=True, id=user_id)

    if user.is_subscribed:
        await c.message.answer(
            "Будьте внимательны❗️ У пользователя есть активная подписка. Если вы сейчас укажите новый тариф для пользователя,"
"то старая подписка будет больше недействительна"
        )

    if user:
        await c.message.answer(
            "Выберите тариф для пользователя",
            reply_markup=get_change_tariff_markup(user_id)
        )
    else:
        await c.answer("Пользователь не найден")


async def ask_tariff_date(c: types.CallbackQuery, state: FSMContext):
    c_data = c.data.split('_')
    tariff = c_data[1]
    user_id = int(c_data[2])

    await state.set_state(ChangeUserTariffFSM.date_state)
    await state.update_data(tariff=tariff, user_id=user_id)

    await c.message.answer(
        "Выберите дату действия подписки по новому тарифу:",
        reply_markup=tariff_date_markup
    )
    await c.answer()


async def ask_date(c: types.CallbackQuery, state: FSMContext):
    await state.set_state(ChangeUserTariffFSM.date_input_state)

    await c.message.answer(
        "Введите дату окончания подписки в формате дд-мм-гггг"
    )
    await c.answer()


async def handle_input_date(m: types.Message, state: FSMContext):
    date_text = m.text

    if date_text:
        try:
            date = datetime.datetime.strptime(date_text, "%d-%m-%Y")

            s_data = await state.get_data()
            await state.clear()

            await change_tariff(
                state_data=s_data,
                date=date
            )

        except ValueError:
            await m.answer("Неверный формат, попробуйте ещё раз")
    else:
        await m.answer("Введите текст!")


async def handle_date(c: types.CallbackQuery, state: FSMContext):
    days = int(c.data.split('_')[1])

    s_data = await state.get_data()
    await state.clear()

    if await change_tariff(state_data=s_data, days=days):
        await c.message.answer(
            "Тариф пользователя успешно изменён!"
        )
    else:
        await c.message.answer(
            "Произошла ошибка, тариф пользователя не изменён. Возможно такого пользователя не существует"
        )

    await c.answer()


@connection
async def change_tariff(state_data: dict, db_session: AsyncSession, days: int = 0, date: datetime.datetime = None) -> bool:
    user = UserDAO.get_obj(session=db_session, id=state_data['user_id'])

    if user:
        await UserService.get_instance().subscribe(
            days=days,
            tariff=SubscribeTariffEnum(state_data["tariff"]),
            user=user,
            expire_date=date
        )

        return True
    else:
        return False



def register_users_manage_handlers(dp: Dispatcher):
    dp.callback_query.register(send_users_list, F.data == "users_manage", AdminFilter())
    UsersPaging.register_paging_handlers(dp=dp)
    dp.callback_query.register(send_user_card, F.data.startswith("user_"))

    # tariff edit
    dp.callback_query.register(ask_changing_tariff, F.data.startswith("changesub_"), AdminFilter())
    dp.callback_query.register(ask_tariff_date, F.data.startswith("changeut_"))
    dp.callback_query.register(ask_date, F.data == "tariffdate_wr", StateFilter(ChangeUserTariffFSM.date_state), AdminFilter())
    dp.message.register(handle_input_date, StateFilter(ChangeUserTariffFSM.date_input_state), AdminFilter())
    dp.callback_query.register(
        handle_date,
        F.data.startswith("tariffdate_"),
        StateFilter(ChangeUserTariffFSM.date_state),
        AdminFilter()
    )

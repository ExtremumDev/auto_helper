from aiogram import types, F, Dispatcher
from sqlalchemy.ext.asyncio import AsyncSession

from src.aiogram_bot.database.utils import provide_user
from src.aiogram_bot.keyboards.user.subscription import get_subscription_manage_markup, tariffs_markup
from src.aiogram_bot.utils.text import get_subscription_info_text
from src.common.database.models.enums import SubscribeTariffEnum
from src.common.database.models.user import User


@provide_user
async def send_account_info(m: types.Message, db_session: AsyncSession, user: User, *args):

    await m.answer(
        get_subscription_info_text(user.is_subscribed, user.sub_tariff, user.expiration_date),
        reply_markup=get_subscription_manage_markup()
    )


async def send_tariffs(c: types.CallbackQuery):
    await c.message.answer(
        "Выберите тариф:",
        reply_markup=tariffs_markup
    )

    await c.answer()


@provide_user
async def send_bill(c: types.CallbackQuery):
    tariff_id = c.data.split('_')[1]

    tariff = SubscribeTariffEnum(tariff_id)

    await c.answer()

def register_subscription_manage_markup(dp: Dispatcher):
    dp.message.register(send_account_info, F.text == "Управление подпиской")
    dp.callback_query.register(send_tariffs, F.data == "buy_sub")

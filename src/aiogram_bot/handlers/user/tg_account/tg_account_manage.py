
from aiogram import types, Dispatcher, F
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession

from src.aiogram_bot.database.utils import provide_user
from src.aiogram_bot.services.data.tg_auth import TelegramAuthManager
from src.common.database.models.enums import TelegramAccountStatus
from src.common.database.models.user import User


@provide_user(load_tg_account=True)
async def send_auth_menu(m: types.Message, user: User, db_session: AsyncSession, *args):

    tg_acc = user.telegram_account

    account_descr_message_data = TelegramAuthManager().get_instance().get_tg_account_descr(tg_account=tg_acc)

    await m.answer(
        text=account_descr_message_data["text"],
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=account_descr_message_data["markup"]
    )


@provide_user(load_tg_account=True)
async def reauthorize_account(c: types.CallbackQuery, user: User, db_session: AsyncSession, *args):
    if user.telegram_account:
        if user.telegram_account.status == TelegramAccountStatus.AUTH_NEEDED:
            send_code_response = await TelegramAuthManager().get_instance().start_code_authentication(
                phone_number=user.telegram_account.phone_number,
                db_session=db_session,
                tg_account=user.telegram_account,
                user=user
            )

            if send_code_response["success"]:
                await c.message.answer(
                    f"Авторизация телефона {user.telegram_account.phone_number}\n" + send_code_response["text"],
                    reply_markup=send_code_response["markup"]
                )
            else:
                await c.message.answer(
                    f"Во время авторизации номера телефона {user.telegram_account.phone_number} возникла ошибка:\n" + send_code_response["text"]
                )

            await c.answer()
        else:
            account_descr_message_data = TelegramAuthManager().get_instance().get_tg_account_descr(tg_account=None)

            await c.message.edit_reply_markup(
                reply_markup=account_descr_message_data["markup"]
            )
            await c.message.edit_text(
                text=account_descr_message_data["text"]
            )
            await c.answer("Ваш аккаунт уже авторизован и готов к работе", show_alert=True)
    else:
        account_descr_message_data = TelegramAuthManager().get_instance().get_tg_account_descr(tg_account=None)

        await c.message.edit_reply_markup(
            reply_markup=account_descr_message_data["markup"]
        )
        await c.message.edit_text(
            text=account_descr_message_data["text"]
        )

        await c.answer("У вас нет авторизованного телеграмм аккаунта")


@provide_user(load_tg_account=True)
async def turn_off_account(c: types.CallbackQuery, db_session: AsyncSession, user: User, *args):
    await c.answer()


def register_tg_account_manage_handlers(dp: Dispatcher):
    dp.message.register(send_auth_menu, F.text == "👤 Управление телеграмм аккаунтом")
    dp.callback_query.register(reauthorize_account, F.data == "complete_acc_auth")
    dp.callback_query.register(turn_off_account, F.data == "turn_off_account")

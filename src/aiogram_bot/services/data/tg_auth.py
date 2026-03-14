from sqlalchemy.ext.asyncio import AsyncSession

from src.aiogram_bot.keyboards.user.tg_auth import get_telegram_account_markup, authorize_markup, get_input_code_markup
from src.aiogram_bot.services.app_messaging import PyrogramAppProcedureCall
from src.aiogram_bot.services.singleton import BaseSingleton
from src.aiogram_bot.utils.text import get_tg_account_info_text
from src.common.database.dao.user import TelegramAccountDAO
from src.common.database.models.enums import TelegramAccountStatus
from src.common.database.models.user import TelegramAccount, User
from src.common.utils.auth import AuthResponseStatus


class TelegramAuthManager(BaseSingleton):

    def check_owner_availabiltiy(self, user: User, tg_account: TelegramAccount):
        """
        :param user: User to check, if he can be an owner of this account
        :param tg_account: Checking account
        :return: True - if account is free() or account is already belong to user
        """
        if user.telegram_account:
            return user.telegram_account.id == tg_account.id
        else:
            if tg_account.user:
                return tg_account.user.id == user.id
            else:
                return True

    def get_tg_account_descr(self, tg_account: TelegramAccount | None):

        if tg_account:
            text = get_tg_account_info_text(
                is_auth=True,
                phone_number=tg_account.phone_number,
                status=tg_account.status
            )
            markup = get_telegram_account_markup(
                is_authorized=tg_account.status != TelegramAccountStatus.AUTH_NEEDED,
                is_message_handling=tg_account.is_message_handling
            )
        else:
            text = get_tg_account_info_text(is_auth=False)
            markup = authorize_markup

        return {
            "text": text,
            "markup": markup
        }

    async def start_code_authentication(
            self, phone_number: str, db_session: AsyncSession, user: User, tg_account: TelegramAccount = None
    ):
        auth_response = await PyrogramAppProcedureCall.get_instance().create_authorize_task(
            phone_number=phone_number
        )

        text = ""
        markup = None
        success = False

        match auth_response.status:
            case AuthResponseStatus.WAITING_CODE:
                if auth_response.tg_account_id:
                    if not tg_account:
                        tg_account = await TelegramAccountDAO.get_account_with_user(
                            db_session=db_session, id=auth_response.tg_account_id
                        )

                    if tg_account and not TelegramAuthManager().get_instance().check_owner_availabiltiy(
                            user=user,
                            tg_account=tg_account
                    ):
                        text = "Аккаунт с этим номером используется другим пользователем"
                    else:
                        if tg_account:
                            user.telegram_account = tg_account
                            await db_session.commit()

                            text = "Введите код подтверждения"
                            markup = get_input_code_markup()
                            success = True
                        else:
                            text = "Произошла неизвестная ошибка, попробуйте ещё раз"
                else:
                    text = "Произошла неизвестная ошибка, попробуйте ещё раз"
            case AuthResponseStatus.INVALID_PHONE:
                text = "Введён неверный номер телефона, не связанный с действующим аккаунтом. Попробуйте еще раз"
            case AuthResponseStatus.FLOOD_WAIT:
                text = "Слишком много попыток! Попробуйте позже"
            case AuthResponseStatus.PHONE_ALREADY_AUTH:
                text = "Аккаунт успешно авторизован!"
                success = True
            case AuthResponseStatus.UNEXPECTED_ERROR:
                text = "Произошла неизвестная ошибка, попробуйте позже или обратитесь к администратору"
        return {
            "text": text,
            "markup": markup,
            "success": success
        }


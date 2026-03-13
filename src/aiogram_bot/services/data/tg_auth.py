from src.common.database.models.user import TelegramAccount, User
from src.common.utils.auth import AuthResponseStatus


class AuthSessionResult:
    def __init__(self, status: AuthResponseStatus, tg_account_id: int | None = None):
        self.status = status
        self.tg_account_id = tg_account_id


class TelegramAuthManager:

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


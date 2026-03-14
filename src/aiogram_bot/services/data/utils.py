from src.common.utils.auth import AuthResponseStatus


class AuthSessionResult:
    def __init__(self, status: AuthResponseStatus, tg_account_id: int | None = None):
        self.status = status
        self.tg_account_id = tg_account_id

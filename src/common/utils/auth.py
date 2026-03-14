from enum import StrEnum


class AuthResponseStatus(StrEnum):
    PHONE_ALREADY_AUTH = "phone_used"
    UNEXPECTED_ERROR = "unexpected"
    SERVER_ERROR = "server"
    INVALID_PHONE = "invalid_phone"
    WAITING_CODE = "code"
    INVALID_CODE = "invalid_code"
    WAITING_PASSWORD = "password"
    INVALID_PASSWORD = "invalid_password"
    FLOOD_WAIT = "flood_wait"
    EXPIRED = "expired"
    SUCCESS = "success"

    @classmethod
    def _missing_(cls, value):
        return cls.UNEXPECTED_ERROR

class GroupAddResponseStatus(StrEnum):
    INVALID_CHAT_TYPE = "type"
    INVALID_CHAT = "invalid"
    SUCCESS = "success"
    UNEXPECTED = "unexpected"
    ACCOUNT_INVALID = "account"

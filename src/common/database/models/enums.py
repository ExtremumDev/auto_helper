from enum import Enum


class TelegramAccountStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inact"
    AUTH_NEEDED = "auth"

class SubscribeTariffEnum(Enum):
    LIGHT = "first"
    MEDIUM = "medium"
    HARD = "hard"
    ELITE = "elite"
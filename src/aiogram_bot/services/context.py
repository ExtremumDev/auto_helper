from dataclasses import dataclass

from src.aiogram_bot.services.app_messaging import PyrogramAppProcedureCall
from src.aiogram_bot.services.data.tg_auth import TelegramAuthManager
from src.aiogram_bot.services.data.user import UserService


@dataclass
class ServiceContext:

    __user_service: UserService
    __app_messaging_service: PyrogramAppProcedureCall
    __tg_auth_manager: TelegramAuthManager

    @classmethod
    def create_defaults(cls):
        cls.__user_service = UserService()
        cls.__app_messaging_service = PyrogramAppProcedureCall(None)
        cls.__tg_auth_manager = TelegramAuthManager()

    @classmethod
    def get_user_service(cls) -> UserService:
        return cls.__user_service

    @classmethod
    def get_app_messaging_service(cls):
        return cls.__app_messaging_service

    @classmethod
    def get_telegram_auth_manager(cls):
        return cls.__tg_auth_manager

from dataclasses import dataclass

from src.aiogram_bot.services.data.user import UserService


@dataclass
class ServiceContext:

    __user_service: UserService

    @classmethod
    def create_defaults(cls):
        cls.__user_service = UserService()

    @classmethod
    def get_user_service(cls) -> UserService:
        return cls.__user_service

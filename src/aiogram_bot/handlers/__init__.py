from aiogram import Dispatcher

from src.aiogram_bot.handlers.admin import register_admin_handlers
from src.aiogram_bot.handlers.user import register_user_handlers


def register_all_handlers(dp: Dispatcher):
    register_admin_handlers(dp)
    register_user_handlers(dp)

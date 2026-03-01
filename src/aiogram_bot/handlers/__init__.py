from aiogram import Dispatcher

from src.aiogram_bot.handlers.admin import register_admin_handlers


def register_all_handlers(dp: Dispatcher):
    register_admin_handlers(dp)

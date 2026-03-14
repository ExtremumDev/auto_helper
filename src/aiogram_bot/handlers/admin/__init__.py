from src.aiogram_bot.handlers.admin.main import register_main_admin_handlers
from src.aiogram_bot.handlers.admin.users_manage import register_users_manage_handlers


def register_admin_handlers(dp):
    register_main_admin_handlers(dp)
    register_users_manage_handlers(dp)
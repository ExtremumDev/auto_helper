from src.aiogram_bot.handlers.user.orders_manage.groups_list_edit import register_groups_list_edit_markup
from src.aiogram_bot.handlers.user.orders_manage.keywords_manage import register_keywords_manage_handlers
from src.aiogram_bot.handlers.user.start import register_start_handlers
from src.aiogram_bot.handlers.user.subscription.sub_manage import register_subscription_manage_markup
from src.aiogram_bot.handlers.user.tg_account.authorize import register_authorization_handlers
from src.aiogram_bot.handlers.user.tg_account.tg_account_manage import register_tg_account_manage_handlers


def register_user_handlers(dp):
    register_start_handlers(dp)

    register_tg_account_manage_handlers(dp)
    register_authorization_handlers(dp)
    register_keywords_manage_handlers(dp)
    register_subscription_manage_markup(dp)
    register_groups_list_edit_markup(dp)

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_admin_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Управление пользователями", callback_data="users_manage")]
    ]
)

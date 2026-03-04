from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_user_reply_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Настройка фильтрации заказов")],
        [KeyboardButton(text="Управление подпиской")]
    ]
)

cancel_inline_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action")]
    ]
)

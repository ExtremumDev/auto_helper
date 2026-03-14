from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_user_reply_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Настройка фильтрации заказов")],
        [KeyboardButton(text="💵 Управление подпиской")],
        [KeyboardButton(text="👤 Управление телеграмм аккаунтом")]
    ],
    resize_keyboard=True
)

main_admin_reply_markup = ReplyKeyboardMarkup(
    keyboard=[
        *main_user_reply_markup.keyboard,
        [KeyboardButton(text="Админ-панель")]
    ],
    resize_keyboard=True
)

cancel_inline_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action")]
    ]
)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_order_manage_markup():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Изменить ключевые слова", callback_data="editw_keywords")
            ],
            [
                InlineKeyboardButton(text="Изменить слова-исключения", callback_data="editw_exceptions")
            ]
        ]
    )
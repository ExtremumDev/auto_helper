from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_subscription_manage_markup():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💸 Оплатить", callback_data="buy_sub")
            ]
        ]
    )

tariffs_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="100 руб в месяц", callback_data="buytariff_light")],
        [InlineKeyboardButton(text="500 руб в месяц", callback_data="buytariff_medium")],
        [InlineKeyboardButton(text="1000 руб в месяц", callback_data="buytariff_hard")],
    ]
)

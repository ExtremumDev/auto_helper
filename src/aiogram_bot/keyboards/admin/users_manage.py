from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_users_manage_markup(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Изменить тариф подписки", callback_data=f"changesub_{user_id}")],
        ]
    )

def get_change_tariff_markup(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="100 руб в месяц", callback_data=f"changeut_light_{user_id}")],
            [InlineKeyboardButton(text="500 руб в месяц", callback_data=f"changeut_medium_{user_id}")],
            [InlineKeyboardButton(text="1000 руб в месяц", callback_data=f"changeut_hard_{user_id}")],
            [InlineKeyboardButton(text="Элит", callback_data=f"changeut_elite_{user_id}")],
        ]
    )


tariff_date_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Неделя", callback_data="tariffdate_7")],
        [InlineKeyboardButton(text="10 дней", callback_data="tariffdate_10")],
        [InlineKeyboardButton(text="Месяц", callback_data="tariffdate_30")],
        [InlineKeyboardButton(text="Указать вручную", callback_data="tariffdate_wr")],
        [InlineKeyboardButton(text="❌ Отменить операцию", callback_data="cancel_action")]
    ]
)

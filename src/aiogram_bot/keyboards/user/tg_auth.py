from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_input_code_markup(cur_code: str = ""):
    # Forming buttons for digits 1-9

    markup = [
        [InlineKeyboardButton(text=f"{cur_code}", callback_data=" ")],
        [],
        [],
        []
    ]
    j = 1
    for i in range(1, 10):
        markup[j].append(InlineKeyboardButton(text=str(i), callback_data=f"code_{cur_code}{i}"))

        if i % 3 == 0:
            j += 1

    markup.extend(
        [
            [
                InlineKeyboardButton(text="⬅️", callback_data="codeerase_" + cur_code),
                InlineKeyboardButton(text="0", callback_data=f"code_{cur_code}0"),
                InlineKeyboardButton(text="✅", callback_data=f"completecode_{cur_code}"),
            ],
            [
                InlineKeyboardButton(text="❌Отмена", callback_data="cancel")
            ]
        ]
    )
    return InlineKeyboardMarkup(
        inline_keyboard=markup
    )

authorization_types_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="По номеру телефона", callback_data="auth_phone")]
    ]
)

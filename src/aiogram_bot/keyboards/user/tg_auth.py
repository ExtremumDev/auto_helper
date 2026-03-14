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

def get_telegram_account_markup(is_authorized: bool, is_message_handling: bool = None):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[

        ]
    )

    if is_authorized:
        markup.inline_keyboard.extend(
            [
                [
                    InlineKeyboardButton(text="⏸ Остановить мониторинг заказов", callback_data="turn_off_orders")
                    if is_message_handling
                    else InlineKeyboardButton(text="▶️ Включить мониторинг заказов", callback_data="turn_on_orders")
                ]
            ],
        )
    else:
        markup.inline_keyboard.extend(
            [
                [
                    InlineKeyboardButton(text="Авторизоваться", callback_data="complete_acc_auth")
                ]
            ]
        )
    markup.inline_keyboard.extend(
        [
            [InlineKeyboardButton(text="❌ Отключить аккаунт", callback_data="turn_off_account")]
        ]
    )

    return markup

authorization_types_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="По номеру телефона", callback_data="auth_phone")]
    ]
)

authorize_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Авторизоваться", callback_data="authorize")]
    ]
)

send_code_again_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отправить код повторно", callback_data="send_code_again")]
    ]
)

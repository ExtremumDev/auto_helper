from datetime import datetime

from src.common.database.models.enums import SubscribeTariffEnum, TelegramAccountStatus


def get_orders_settings_descr(keywords: str, except_words: str):
    text = f"""
Ключевые слова для отбора заказов:
{keywords if keywords else 'Не указаны'}

Слова-исключения:
{except_words if except_words else 'Не указаны'}
"""

    return text


def get_tariff_display_name(tariff: SubscribeTariffEnum) -> str:
    if tariff == SubscribeTariffEnum.LIGHT:
        return "100 руб в месяц"
    elif tariff == SubscribeTariffEnum.MEDIUM:
        return "500 руб в месяц"
    elif tariff == SubscribeTariffEnum.HARD:
        return "1000 руб в месяц"
    elif tariff == SubscribeTariffEnum.ELITE:
        return "Элит"
    return "Тариф"


def get_subscription_info_text(is_subscribed: bool, tariff: SubscribeTariffEnum, expire_date: datetime):
    text = """
Подписка: {is_active}, {tariff_name}
"""
    if is_subscribed:
        text += f"\nИстекает: {expire_date}"

    return text.format(
        is_active="Активна" if is_subscribed else "Не активна",
        tariff_name=get_tariff_display_name(tariff) if is_subscribed else ""
    )

def get_tg_account_info_text(
    is_auth: bool, phone_number: str = None, status: TelegramAccountStatus = None
):
    text = ""
    if is_auth:
        if status == TelegramAccountStatus.ACTIVE or status == TelegramAccountStatus.INACTIVE:
            text += "🟢 Телеграмм аккаунт авторизирован"
        elif status == TelegramAccountStatus.AUTH_NEEDED:
            text += r"🕑 Телеграмм аккаунт привязан, не авторизирован\. Пройдите авторизацию"

        text += fr"""
Данные аккаунта:
📞 Номер телефона \- `{phone_number}`
"""

        if status == TelegramAccountStatus.ACTIVE:
            text += "\n🟢 Мониторинг сообщений включён"
        else:
            text += "\n🔴 Мониторинг сообщений выключён"
    else:
        text += r"🔴 Телеграмм аккаунт не авторизирован\. Мониторинг групп не доступен\. Пройдите авторизацию по кнопке ниже👇"

    return text

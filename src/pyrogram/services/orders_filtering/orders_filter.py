import re

from typing import List

from src.common.database.models.user import User


def check_keywords_in_text(text: str, keywords: List[str]):

    pattern = '|'.join(re.escape(keyword) for keyword in keywords)
    regex = re.compile(pattern)
    return bool(regex.search(text))


def is_order_suitable_for_user(user: User, order_text: str):
    res = False
    if user.order_keywords:
        res = res and check_keywords_in_text(order_text, user.order_keywords.split(','))

    if user.except_words:
        res = res and not check_keywords_in_text(order_text, user.except_words.split(','))
    return res
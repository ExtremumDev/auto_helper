import re


def search_keywords_in_text(text: str, keywords: str) -> bool:
    """

    :param text: Source text to search words in
    :param keywords: Keywords that must be searched
    :return: True - if even one keyword was found, False - else
    """

    pattern = '|'.join(re.escape(keyword) for keyword in keywords)
    regex = re.compile(pattern)
    return bool(regex.search(text))
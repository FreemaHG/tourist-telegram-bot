from typing import Union

from loguru import logger


def func_address_conversion(string: str) -> Union[str, bool]:
    """
    Функция преобразует строку вида 'Манхэттен, <span class='highlighted'>Нью-Йорк</span>, Нью-Йорк, США'
    в читаемую 'Манхэттен, Нью-Йорк, США
    """
    logger.info(f"преобразование строки | входные данные: {string}")

    try:
        result = string.replace("<span class='highlighted'>", "").replace("</span>", "")
        logger.info(f"преобразование строки | возвращаем строку: {result}")
        return result

    except TypeError as e:
        logger.exception(e)  # Подробный вывод ошибки в логе
        return False

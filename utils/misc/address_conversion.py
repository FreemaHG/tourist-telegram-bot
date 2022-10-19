from loguru import logger


def func_address_conversion(string: str) -> str:
    """
    Функция преобразует строку вида 'Манхэттен, <span class='highlighted'>Нью-Йорк</span>, Нью-Йорк, США'
    в читаемую 'Манхэттен, Нью-Йорк, США
    """
    logger.info(f"преобразование строки | входные данные: {string}")
    result = string.replace("<span class='highlighted'>", "").replace("</span>", "")
    logger.info(f"преобразование строки | возвращаем строку: {result}")

    return result

import re
from loguru import logger  # Для логирования


def func_address_conversion(string: str) -> str:
    """
    Функция преобразует строку вида 'Манхэттен, <span class='highlighted'>Нью-Йорк</span>, Нью-Йорк, США'
    в читаемую 'Манхэттен, Нью-Йорк, США
    """
    logger.info(f"преобразование строки | входные данные: {string}")
    words_list = string.split(' ')
    pattern = re.compile(r'>(.*)<')
    result_line = ''
    for word in words_list:
        if '<' not in word:
            result_line += word + ' '
        else:
            correct_world = pattern.search(word)
            if correct_world is not None:
                result_line += correct_world.group(1) + ', '

    result = result_line[:-1]

    logger.info(f"преобразование строки | возвращаем строку: {result}")
    return result

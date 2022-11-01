from typing import List


def func_chunks_generators(data_list: List[int], number: int):
    """
    Функция разбивает переданный список с элементами на подсписки с кол-вом элементов, равным переданному значению
    """

    for i in range(0, len(data_list), number):
        yield data_list[i: i + number]

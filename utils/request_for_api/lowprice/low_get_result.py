from utils.request_for_api.lowprice.low_get_location import get_id_location
from utils.request_for_api.lowprice.low_get_hostels import get_id_hostels
from utils.request_for_api.lowprice.low_get_photos import preparation_photos
from utils.request_for_api.api_request import request_to_api

from multiprocessing.pool import ThreadPool
import multiprocessing
from loguru import logger


def get_result(id_location: int, number_of_hotels: int, number_of_photos: int = 0):
    """ Получение результатов по переданным данным """

    logger.info('Подготовка данных для пользователя')

    # Возврат данных из БД, если есть, либо

    # Сохраняем все данные в БД
    # Потом SQL-запросом извлекаем нужные данные

    # Получаем id отелей нужной локации
    id_hostels_list = get_id_hostels(id_location)

    if not id_hostels_list:
        logger.error('отели не получены')
        return False

    # ТЕСТИРУЕМЫЙ МОМЕНТ
    # Нужно получить ответ от функции (True / False - успешно или нет)
    if len(id_hostels_list) > 1:  # Если несколько отелей, запускаем многопоточную загрузку фото
        logger.info('Многопоточная загрузка фото отелей')

        pool = ThreadPool(
            processes=multiprocessing.cpu_count() * 5)  # Запускаем потоков в 5 раз больше, чем есть у нас ядер

        # Ответ сервера 429 - слишком много запросов (одновременно 25 запросов по отелям)
        async_response = pool.map(preparation_photos, id_hostels_list)

        pool.close()  # Обязательно закрываем объект Pool
        pool.join()

    else:
        logger.info('Обычная загрузка фото отелей')
        preparation_photos(id_hostels_list[0])







    # return_response = async_response.get()  # Нужно ли???

    # for id_hotel in id_hostels_list:
    #     async_response = pool.apply_async(get_and_save_photos, id_hotel)  # Ошибка - вместо id_hotel должен быть итерируемый объект
    #     return_response = async_response.get()  # Нужно ли???



    # print('Результат:', async_response)

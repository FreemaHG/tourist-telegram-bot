from utils.request_for_api.get_hostels import get_hostels
from utils.request_for_api.get_photos import preparation_photos
from database.check_data.check_hotels import check_hotels_by_id_location  # Проверка отеля в БД
from database.get_data.get_photos import get_photos_of_hotel

from multiprocessing.pool import ThreadPool
import multiprocessing
from threading import Lock
from loguru import logger
import time
from typing import Union, List
from datetime import date

from utils.misc.list_divider import func_chunks_generators


LOCK = Lock()  # Для избежания ошибок при сохранении данных в БД в разных потоках


# ПРОВЕРИТЬ СОРТИРОВКУ ПО ЦЕНЕ И КОЛ-ВО СОХРАНЯЕМЫХ ОТЕЛЕЙ!!!
def get_result(
        command: str,
        id_location: int,
        check_in_date: Union[date, None],
        check_out_date: Union[date, None],
        number_of_hotels: int,
        number_of_photos: Union[int, None]) -> Union[List, bool]:

    """ Получение результатов по переданным данным """

    result_list = []  # Список с отелями
    logger.info('Подготовка данных для пользователя')

    # Проверка отелей в БД
    hotels = check_hotels_by_id_location(id_location, command)

    # Если в БД нет данных, выполняем запрос к API и сохраняем данные по отелям
    if not hotels:
        logger.info('В БД нет данных по отелям локации. Получение данных от API')
        id_hostels_list = get_hostels(id_location, check_in_date, check_out_date)

        if not id_hostels_list:
            logger.error('Отели не получены от API')
            return False

        # Разбиваем список с id отелями на списки по 5 элементов (т.к. у API отграничение в 5 одновременных запросов)
        total_list = func_chunks_generators(id_hostels_list, 5)
        count = 0

        # Многопоточная загрузка фото
        with LOCK:  # Замок для сессии (во избежания ошибок при сохранении данных в БД)
            start = time.time()
            for data in list(total_list):
                # На каждой итерации создаем новый поток (во избежания ошибки: ValueError: Pool not running)
                parent_pool = ThreadPool(
                    processes=multiprocessing.cpu_count() * 5)  # Запускаем потоков в 5 раз больше, чем есть у нас ядер
                count += 1
                logger.info(f'thread | {count} партия запросов к API')
                async_response = parent_pool.map(preparation_photos, data)
                parent_pool.close()  # Обязательно закрываем объект Pool
                parent_pool.join()

                if False in async_response:
                    logger.warning('thread | не все фото были загружены ')

                time.sleep(0.5)  # Задержка в 0.5 сек между запросами к API

            logger.debug(f'Затраченное время на сохранение фото: {time.time() - start} сек')

    # Повторная проверка отелей в БД
    hotels = check_hotels_by_id_location(id_location, command)

    if len(hotels) > number_of_hotels:  # Возможно len(hotels) не работает!!!
        hotels = hotels[:number_of_hotels]  # Убираем лишние результаты

    for hotel in hotels:
        if number_of_photos is not None:
            number_of_photos = int(number_of_photos)
            hotel_photos, rooms_photos = get_photos_of_hotel(hotel.id, number_of_photos)  # Получаем фото отеля

            if not hotel_photos or not rooms_photos:
                logger.warning('нет фото отеля, имеющегося в БД')
                preparation_photos(hotel.id)
                hotel_photos, rooms_photos = get_photos_of_hotel(hotel.id, number_of_photos)  # Получаем фото отеля

            photos = hotel_photos + rooms_photos

        else:
            photos = None

        # Подготавливаем нужные данные для вывода пользователю
        result_list.append(
            {
                'id': hotel.id,
                'hotel': hotel.name,
                'address': hotel.address,
                'distance_to_center': hotel.distance_to_center,
                'price': hotel.price,
                'photos': photos
            }
        )

    return result_list

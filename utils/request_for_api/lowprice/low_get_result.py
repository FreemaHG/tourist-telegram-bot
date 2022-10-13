from utils.request_for_api.lowprice.low_get_location import get_id_location
from utils.request_for_api.lowprice.low_get_hostels import get_id_hostels
from utils.request_for_api.lowprice.low_get_photos import get_and_save_photos
from utils.request_for_api.api_request import request_to_api

from multiprocessing.pool import ThreadPool
import multiprocessing


def get_result(location: str, number_of_hotels: int, number_of_photos: int = 0):
    """ Получение результатов по переданным данным """

    # Возможно вначале поиск в БД по локации для вывода вариантов, если нет совпадений, то запуск функций с вызовом API!!!

    # Получаем id указанной локации
    id_location = get_id_location(location)

    if not id_location:
        return False

    # Получаем id отелей нужной локации
    id_hostels_list = get_id_hostels(id_location)

    if not id_hostels_list:
        return False

    # Многопоточная загрузка и сохранение фото
    pool = ThreadPool(
        processes=multiprocessing.cpu_count() * 5)  # Запускаем потоков в 5 раз больше, чем есть у нас ядер

    for id_hotel in id_hostels_list:
        async_response = pool.apply_async(get_and_save_photos, id_hotel)
        return_response = async_response.get()  # Нужно ли???




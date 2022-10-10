from utils.request_for_api.lowprice.low_get_location import get_id_location
from utils.request_for_api.lowprice.low_get_hostels import get_id_hostels


def get_result(location: str, number_of_hotels: int, number_of_photos: int = 0):
    """ Получение результатов по переданным данным """

    # Возможно вначале поиск в БД по локации для вывода вариантов, если нет совпадений, то запуск функций с вызовом API!!!

    id_location = get_id_location(location)  # Получаем id указанной локации

    if not id_location:
        return False

    id_hostels_list = get_id_hostels(id_location)  # Получаем id отелей нужной локации

    if not id_hostels_list:
        return False
    else:
        print('id_hostels_list:', id_hostels_list)

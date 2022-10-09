from utils.request_for_api.lowprice.low_get_location import get_id_location


def get_result(location: str, number_of_hotels: int, number_of_photos: int = 0):
    """ Получение результатов по переданным данным """

    id_location = get_id_location(location)  # Получаем id указанной локации

    if not id_location:
        return False

    # id_hostels_list = get_id_hostels(id_location)  # Получаем id отелей нужной локации
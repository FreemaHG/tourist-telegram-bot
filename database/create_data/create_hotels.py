from database.create_db import Hotels, session
from loguru import logger
from typing import Union


def create_new_hotel(
        id_hotel: int,
        id_location: int,
        name: str,
        address: Union[str, bool],
        distance_to_center:
        Union[str, bool],
        price: Union[float, bool]):

    """ Создаем новую запись об отеле в БД """

    # Обязательные параметры
    new_hotel = Hotels(
            id=id_hotel,
            id_location=id_location,
            name=name
        )

    # Проверка не обязательных параметров (могут не встречаться в ответе от API)
    if address:
        new_hotel.address = address

    if distance_to_center:
        new_hotel.distance_to_center = distance_to_center

    if price:
        new_hotel.price = price

    session.merge(new_hotel)  # Сохраняем данные (только новые) в текущей сессии
    logger.debug(f'db | сохранение данных в сессии | id: {id_hotel}, название: {name}')

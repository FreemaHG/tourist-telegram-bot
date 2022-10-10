from database.create_db import Hotels, session
from loguru import logger
from typing import Union


def create_new_hotel(
        id_hotel: int, id_location: int, name: str, address: str, distance_to_center: Union[str, bool], price: float):
    """ Создаем новую запись об отеле в БД """

    if distance_to_center is False:
        new_hotel = Hotels(
            id=id_hotel,
            id_location=id_location,
            name=name,
            address=address,
            price=price
        )

    else:
        new_hotel = Hotels(
            id=id_hotel,
            id_location=id_location,
            name=name,
            address=address,
            distance_to_center=distance_to_center,
            price=price
        )

    logger.debug(f'сохранение нового отеля в текущей сессии | id: {id_hotel}, название: {name}')
    session.merge(new_hotel)  # Сохраняем данные (только новые) в текущей сессии

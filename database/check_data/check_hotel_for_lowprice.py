from database.create_db import Hotels, session
from loguru import logger
from typing import Union, List


def check_hotels_by_id_location(id_location: int) -> Union[List, bool]:
    """ Проверка отелей в БД по id локации """

    hotels = session.query(Hotels).filter(Hotels.id_location == id_location).all()

    if hotels is None:
        logger.warning(f'db поиск отелей | id локации: {id_location}, результатов не найдено')
        return False

    logger.info(f'db поиск отелей | id локации: {id_location}, найдены совпадения')

    return hotels


def check_hotel(id_hotel: int) -> Union[int, bool]:
    """ Проверка отеля в БД """

    hotel = session.query(Hotels).filter(Hotels.id == id_hotel).one_or_none()

    if hotel is None:
        logger.info(f'db поиск отеля | id отеля: {id_hotel}, результатов не найдено')
        return False

    logger.info(f'db поиск отеля | id отеля: {id_hotel}, найдены совпадения')

    return hotel.id

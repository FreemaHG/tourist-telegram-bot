from database.create_db import Hotels, session
from loguru import logger
from typing import Union, List
from sqlalchemy import and_


def check_hotels_by_id_location(
        id_location: int,
        command: str,
        min_price: Union[str, None],
        max_price: Union[str, None],
        min_distance_to_center: Union[str, None],
        max_distance_to_center: Union[str, None]
) -> Union[List, bool]:

    """ Проверка отелей в БД по id локации """

    if command == '/lowprice':
        logger.info(f'db поиск отелей (/lowprice) | сортировка по возрастанию цены')
        hotels = session.query(Hotels).filter(Hotels.id_location == id_location).order_by(Hotels.price).all()

    elif command == '/highprice':
        hotels = session.query(Hotels).filter(Hotels.id_location == id_location).order_by(Hotels.price.desc()).all()
        logger.info(f'db поиск отелей (/highprice) | сортировка по убыванию цены')

    elif command == '/bestdeal':
        if None in [min_price, max_price, min_distance_to_center, max_distance_to_center]:
            logger.error(f'Один из ключевых параметров отсутствует: '
                         f'min_price - {min_price}, max_price - {max_price},'
                         f'min_distance_to_center - {min_distance_to_center}, '
                         f'max_distance_to_center - {max_distance_to_center}')
            return False

        hotels = session.query(Hotels).filter(
            Hotels.id_location == id_location,
            and_(Hotels.distance_to_center >= float(min_distance_to_center),
                 Hotels.distance_to_center <= float(max_distance_to_center)),
            and_(Hotels.price >= float(min_price), Hotels.price <= float(max_price))
        ).order_by(Hotels.price, Hotels.distance_to_center).all()
        logger.info(f'db поиск отелей (/bestdeal) | сортировка по возрастанию цены и расстояния до центра')

    else:
        logger.warning(f'db поиск отелей | команда не распознана: command - {command}')
        return False

    if not hotels:
        logger.warning(f'db поиск отелей | id локации: {id_location}, результатов не найдено')
        return False

    logger.info(f'db поиск отелей | id локации: {id_location}, найдены совпадения')
    return hotels


# Используется ли!?
def check_hotel(id_hotel: int) -> Union[int, bool]:
    """ Проверка отеля в БД """

    hotel = session.query(Hotels).filter(Hotels.id == id_hotel).one_or_none()

    if hotel is None:
        logger.info(f'db поиск отеля | id отеля: {id_hotel}, результатов не найдено')
        return False

    logger.info(f'db поиск отеля | id отеля: {id_hotel}, найдены совпадения')
    return hotel.id

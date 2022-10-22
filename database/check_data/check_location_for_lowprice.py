from database.create_db import Locations, session
from loguru import logger
from sqlalchemy import or_
from typing import Union, List


def check_location(location_name: str) -> Union[List, bool]:
    """ Проверка локации в БД """

    location_name = location_name.capitalize()  # Первая буква заглавная

    # Проверить поиск с разными регистрами
    # contains - поиск частичного совпадения названия переданной локации в адресе локаций в БД
    location = session.query(Locations)\
        .filter(or_(location_name == Locations.name, Locations.location.contains(location_name)))\
        .all()

    if location is None:
        logger.warning(f'db поиск локации | id локации: {location_name}, результатов не найдено')
        return False

    logger.info(f'db поиск локации | id локации: {location_name}, найдены совпадения')
    return location

from database.create_db import Locations, session
from typing import Union, List
from loguru import logger
from sqlalchemy import or_


def check_location(location_name: str) -> Union[List, bool]:
    """ Проверка локации в БД по переданному названию """

    location_name = location_name.capitalize()  # Первая буква заглавная

    # contains - поиск частичного совпадения названия переданной локации в адресе локаций в БД
    location = session.query(Locations)\
        .filter(or_(location_name == Locations.name, Locations.location.contains(location_name)))\
        .all()

    if not location:
        logger.warning(f'db поиск локации | id локации: {location_name}, результатов не найдено')
        return False

    logger.info(f'db поиск локации | id локации: {location_name}, найдены совпадения')
    return location

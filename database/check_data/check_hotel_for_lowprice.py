from database.create_db import Hotels, session
from loguru import logger


def check_location(id_hotel: int) -> bool:
    """ Проверка отеля в БД """

    hotel = session.query(Hotels).filter(Hotels.id == id_hotel).one_or_none()

    if hotel is None:
        logger.info(f'поиск отеля в БД | входные параметры: {id_hotel}, результатов не найдено')
        return False

    logger.info(f'поиск отеля в БД | входные параметры: {id_hotel}, найдены совпадения')
    return hotel.id

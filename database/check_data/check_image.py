from database.create_db import Photos, session
from loguru import logger


def check_img(id_img: int) -> bool:
    """ Проверка фото по id """

    photo = session.query(Photos).filter(Photos.id == id_img).one_or_none()

    if photo is None:
        logger.warning(f'db поиск фото | id фото: {id_img}, результатов не найдено')
        return False

    logger.info(f'db поиск фото | id фото: {id_img}, найдены совпадения')
    return True

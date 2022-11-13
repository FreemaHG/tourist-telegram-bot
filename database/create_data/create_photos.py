from loguru import logger
from sqlalchemy.exc import IntegrityError, PendingRollbackError

from database.create_db import Photos, session


def create_new_photo(id_photo: int, id_hotel: int, url: str, type_photo: str) -> None:
    """ Создаем новую запись с фото в БД """

    new_photo = Photos(
        id=id_photo,
        id_hotel=id_hotel,
        url=url,
        type=type_photo
    )

    try:
        session.add(new_photo)  # Сохраняем данные в текущей сессии
        session.commit()
        logger.debug(f'db | сохранение фото в БД, id: {id_photo}')
    except IntegrityError:
        logger.warning(f'дубликат фото | id фото: {id_photo}')
        session.rollback()  # Откат сессии
    except PendingRollbackError:
        logger.warning(f'откат сессии из-за дубляжа фото | id фото: {id_photo}')


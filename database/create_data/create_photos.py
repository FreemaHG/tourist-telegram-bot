from database.create_db import Photos, session
from database.check_data.check_image import check_img
from loguru import logger
from sqlalchemy.exc import IntegrityError


def create_new_photo(id_photo: int, id_hotel: int, url: str, type_photo: str) -> None:
    """ Создаем новую запись с фото в БД """

    # Проверка фото по id в БД
    if check_img(id_photo) is False:
        new_photo = Photos(
            id=id_photo,
            id_hotel=id_hotel,
            url=url,
            type=type_photo
        )

        try:
            session.merge(new_photo)  # Сохраняем данные в текущей сессии
            session.commit()
            logger.debug(f'db | сохранение фото, id: {id_photo}')
        except IntegrityError:
            logger.warning(f'дубликат фото | id фото: {id_photo}')

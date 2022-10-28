from database.create_db import History, session
from loguru import logger
from typing import Union
from datetime import datetime


# ДОПОЛНИТЬ СОХРАНЕНИЕМ НАЙДЕННЫХ ОТЕЛЕЙ
def create_new_history(user_id: int, command: str, date_of_entry: datetime):
    """ Сохраняем историю запроса пользователя """

    new_history = History(
        user_id=user_id,
        command=command,
        date_of_entry=date_of_entry
    )
    logger.debug(f'db | сохранение истории: user_id: {user_id}, command: {command}, date_of_entry: {date_of_entry}')

    session.add(new_history)
    session.commit()

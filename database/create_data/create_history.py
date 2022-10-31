from database.create_db import History, Association, session
from loguru import logger
from typing import Union
from datetime import datetime
from typing import List


def create_new_history(user_id: int, command: str, date_of_entry: datetime) -> History:
    """ Сохраняем историю запроса пользователя """

    logger.info(f'вызов функции для сохранения истории запроса')

    new_history = History(
        user_id=user_id,
        command=command,
        date_of_entry=date_of_entry
    )

    logger.debug(f'db | добавление истории в сессию: user_id: {user_id}, command: {command}, date_of_entry: {date_of_entry}')
    return new_history

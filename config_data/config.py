import os

from dotenv import load_dotenv, find_dotenv

# Функция find_dotenv возвращает путь к файлу .env, если такой есть
if not find_dotenv():
    # Если файла с настройками бота нет, завершается работа python с соответствующим сообщением
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')  # Импортируем токен из переменных окружения (хранятся в .env)
RAPID_API_KEY = os.getenv('RAPID_API_KEY')

DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку")
)

CUSTOM_COMMANDS = (
    ('lowprice', "ТОП дешевых отелей в городе"),
    ('highprice', "ТОП дорогих отелей в городе"),
    ('bestdeal', "ТОП отелей по цене и расположению от центра"),
    ('history', "История поиска")
)

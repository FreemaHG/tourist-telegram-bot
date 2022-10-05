import os
from dotenv import load_dotenv, find_dotenv

# Функция find_dotenv возвращает путь к файлу .env, если такой есть
if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')  # Если файла с настройками бота нет, завершается работа python с соответствующим сообщением
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')  # Импортируем токен из переменных окружения (хранятся в .env)
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ('lowprice', "Вывести самые дешевые отели в городе"),
    ('highprice', "Вывести самые дорогие отели в городе"),
    ('bestdeal', "Вывести отели, наиболее подходящие по цене и расположению от центра"),
    ('history', "Вывести историю поиска отелей")
)

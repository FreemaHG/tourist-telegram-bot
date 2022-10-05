from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config  # Импортируем конфигурацию бота (токен)


# В loader подгружаются нужные для импорта переменные
storage = StateMemoryStorage()  # Отвечает за хранение состояния пользователя внутри сценария
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)  # Глобальная переменная для хранения бота / state_storage - указываем хранилище для состояний пользователей


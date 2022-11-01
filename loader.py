from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config  # Импортируем конфигурацию бота (токен)


# В loader подгружаются нужные для импорта переменные
storage = StateMemoryStorage()  # Отвечает за хранение состояния пользователя внутри сценария
# Инициализируем бота / state_storage - хранилище для состояний пользователей
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)

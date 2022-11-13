from telebot.custom_filters import StateFilter  # Для поддержки ботом состояний

from loader import bot  # Импортируем бота из файла loader.py
from database.create_db import Base, engine
from utils.set_bot_commands import set_commands
import handlers  # Отработка скриптов по командам (не удалять!!!)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    bot.add_custom_filter(StateFilter(bot))  # Включаем в боте поддержку состояний
    set_commands(bot)  # Устанавливаем команды
    bot.infinity_polling()  # Всегда проверяем обновления (новые сообщения)

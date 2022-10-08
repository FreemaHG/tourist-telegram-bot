from loader import bot  # Импортируем бота из файла loader.py
import handlers  # Импорт папки-обработчика сообщений
from database.create_db import Base, engine
from telebot.custom_filters import StateFilter  # Импортируем StateFilter для поддержки ботом состояний
from utils.set_bot_commands import set_default_commands, set_custom_commands

# Запускаем бота
if __name__ == '__main__':
    Base.metadata.create_all(engine)  # Создаем БД при первом запуске бота (проверить, что БД не перезаписывается!!!)
    bot.add_custom_filter(StateFilter(bot))  # Включаем в боте поддержку состояний
    set_default_commands(bot)  # Устанавливаем стандартные команды
    set_custom_commands(bot)  # Устанавливаем кастомные команды
    bot.infinity_polling()  # Всегда проверяем обновления (новые сообщения)


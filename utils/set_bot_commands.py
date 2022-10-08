from telebot.types import BotCommand
from config_data.config import DEFAULT_COMMANDS, CUSTOM_COMMANDS


def set_default_commands(bot):
    bot.set_my_commands(
        [BotCommand(*i) for i in DEFAULT_COMMANDS],  # Устанавливаем стандартные команды бота (при вводе / будут выводиться возможные команды в телеграмме)
    )


def set_custom_commands(bot):
    bot.set_my_commands(
        [BotCommand(*i) for i in CUSTOM_COMMANDS]  # Устанавливаем кастомные команды бота (при вводе / будут выводиться возможные команды в телеграмме)
    )

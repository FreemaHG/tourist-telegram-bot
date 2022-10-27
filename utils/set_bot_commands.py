from telebot.types import BotCommand
from config_data.config import DEFAULT_COMMANDS, CUSTOM_COMMANDS

COMMANDS = DEFAULT_COMMANDS + CUSTOM_COMMANDS  # Все команды для бота


def set_commands(bot):
    """ Устанавливаем команды бота (при вводе / будут выводиться возможные команды в телеграмме) """
    bot.set_my_commands(
        [BotCommand(*i) for i in COMMANDS]
    )

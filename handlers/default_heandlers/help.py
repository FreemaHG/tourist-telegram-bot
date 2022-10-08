from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS, CUSTOM_COMMANDS
from loader import bot


@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    default_commands = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    custom_commands = [f'/{command} - {desk}' for command, desk in CUSTOM_COMMANDS]
    all_commands = default_commands + custom_commands
    bot.reply_to(message, '\n'.join(all_commands))

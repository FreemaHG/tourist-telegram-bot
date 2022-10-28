from telebot.types import Message
from loader import bot
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import datetime


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.reply_to(message, f"*Привет*, {message.from_user.full_name}!", parse_mode='Markdown')

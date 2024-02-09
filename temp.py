# main.py

import telebot
from hello import handle_start
from zadachi_razrab import test_start

# Токен бота, который вы получите у BotFather в Telegram
bot_token = '6021520913:AAHto-SguBTJW1ctDhPiyuG55SPox3VmPDU'

bot = telebot.TeleBot(bot_token)

# Словарь для хранения информации о пользователях
user_data = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    handle_start(bot, message, user_data)

# Обработчик для начала тестирования
bot.message_handler(func=lambda message: True)
def handle_message(message):
    test_start(bot, message, user_data)

# Запускаем бота
if __name__ == "__main__":
    bot.polling(none_stop=True)

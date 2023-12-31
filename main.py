import os
import requests
import telebot


with open('token.txt', 'r') as file:
    token = file.read().strip()

# Инициализация бота
bot = telebot.TeleBot(token)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Готов!")

# Обработчик всех сообщений пользователя
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)

# Запуск бота
bot.polling()
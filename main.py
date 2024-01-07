import telebot
from telebot import types
import random

with open('token.txt', 'r') as file:
    token = file.read().strip()

bot = telebot.TeleBot(token)

number_to_guess = None 
guess_range = (1, 100)

users = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Привет! Я бот-предсказатель возраста и имени. Введи /name и /age для начала.")

@bot.message_handler(commands=['name'])
def handle_name(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите ваше имя:")
    bot.register_next_step_handler(message, save_name)

def save_name(message):
    chat_id = message.chat.id
    name = message.text
    users[chat_id] = {'name': name}
    bot.send_message(chat_id, f"Спасибо! Ваше имя сохранено как {name}. Теперь введите /age.")

@bot.message_handler(commands=['age'])
def handle_age(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите ваш возраст:")
    bot.register_next_step_handler(message, save_age, chat_id)

def save_age(message, chat_id):
    try:
        age = int(message.text)
        if chat_id not in users:
            users[chat_id] = {}
        users[chat_id]['age'] = age
        bot.send_message(chat_id, f"Спасибо! Ваш возраст сохранен как {age}.")
    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите корректный возраст (целое число).")
        
@bot.message_handler(commands=['help'])
def handle_help(message):
    chat_id = message.chat.id
    help_text = (
        "Список команд:\n"
        "/start - Начать\n"
        "/name - Ввести имя\n"
        "/age - Ввести возраст\n"
        "/help - Справка\n"
        "/predict - Получить предсказание\n"
        "/minigame - Мини-игра \"угадайка\""
    )
    bot.send_message(chat_id, help_text)

@bot.message_handler(commands=['predict'])
def handle_predict(message):
    chat_id = message.chat.id
    if chat_id in users:
        user_data = users[chat_id]
        name = user_data.get('name')
        age = user_data.get('age')
        if name and age:
            random_year = random.randint(2024, 2124)  
            future_age = random_year - 2024 + age  
            prediction_text = f"Я вижу, вижу, что Вам, {name}, в {random_year} будет {future_age}!"
            bot.send_message(chat_id, prediction_text)
        else:
            bot.send_message(chat_id, "Пожалуйста, сначала введите /name и /age.")
    else:
        bot.send_message(chat_id, "Пожалуйста, сначала введите /name и /age.")


@bot.message_handler(commands=['minigame'])
def minigame(message):
    global number_to_guess 
    global guess_range
    guess_range = (1, 100)
    chat_id = message.chat.id
    bot.send_message(chat_id, "Загадай число от 1 до 100, а я буду пытаться угадать.")
    number_to_guess = random.randint(guess_range[0], guess_range[1])
    send_guess_keyboard(chat_id)

def send_guess_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=3)
    bigger_button = types.InlineKeyboardButton("Больше", callback_data="bigger")
    smaller_button = types.InlineKeyboardButton("Меньше", callback_data="smaller")
    equal_button = types.InlineKeyboardButton("Правильно", callback_data="equal")
    markup.add(bigger_button, equal_button, smaller_button)
    bot.send_message(chat_id, f"Ты загадал число "+str(number_to_guess), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    global number_to_guess  
    global guess_range
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.message:
        if call.data == "bigger":
            bot.answer_callback_query(call.id)
            if number_to_guess == guess_range[1]:  
                bot.send_message(chat_id, "Число уже максимальное.")
            else:
                guess_range = (number_to_guess + 1, guess_range[1])
                number_to_guess = random.randint(guess_range[0], guess_range[1])
                send_guess_keyboard(chat_id)
        elif call.data == "smaller":
            bot.answer_callback_query(call.id)
            if number_to_guess == guess_range[0]: 
                bot.send_message(chat_id, "Число уже минимальное.")
            else:
                guess_range = (guess_range[0], number_to_guess - 1)
                number_to_guess = random.randint(guess_range[0], guess_range[1])
                send_guess_keyboard(chat_id)
        elif call.data == "equal":
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "Ура! Я угадал число.")
            bot.delete_message(chat_id, message_id)


def send_start_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    greet_button = types.KeyboardButton('Поздороваться в ответ')
    commands_button = types.KeyboardButton('Что ты умеешь?')
    markup.add(greet_button, commands_button)
    bot.send_message(chat_id, "Привет! Чем могу помочь?", reply_markup=markup)

@bot.message_handler(commands=['hello'])
def handle_start(message):
    chat_id = message.chat.id
    user = message.from_user
    bot.send_message(chat_id, f"Привет, {user.first_name} {user.last_name}!")
    send_start_keyboard(chat_id)

@bot.message_handler(func=lambda message: message.text == 'Поздороваться в ответ')
def greet_user(message):
    bot.reply_to(message, "У тебя хорошие манеры!")

@bot.message_handler(func=lambda message: message.text == 'Что ты умеешь?')
def show_commands(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    help_button = types.KeyboardButton('/help')
    minigame_button = types.KeyboardButton('/minigame')
    back_button = types.KeyboardButton('Назад')
    markup.add(help_button, minigame_button, back_button)
    bot.send_message(chat_id, "Выберите команду:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Назад')
def back_to_main_menu(message):
    chat_id = message.chat.id
    send_start_keyboard(chat_id)

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)

bot.polling()
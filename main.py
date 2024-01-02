import telebot
from telebot import types
import random

# Загрузка токена из файла token.txt
with open('token.txt', 'r') as file:
    token = file.read().strip()

# Инициализация бота
bot = telebot.TeleBot(token)

# Словарь для хранения данных пользователей
users = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Привет! Я бот-предсказатель возраста и имени. Введи /name и /age для начала.")

# Обработчик команды /name
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

# Обработчик команды /age
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
        
# Обработчик команды /help
@bot.message_handler(commands=['help'])
def handle_help(message):
    chat_id = message.chat.id
    help_text = (
        "Список команд:\n"
        "/start - Начать\n"
        "/name - Ввести имя\n"
        "/age - Ввести возраст\n"
        "/help - Справка\n"
        "/predict - Получить предсказание"
    )
    bot.send_message(chat_id, help_text)

# Обработчик команды /predict
@bot.message_handler(commands=['predict'])
def handle_predict(message):
    chat_id = message.chat.id
    if chat_id in users:
        user_data = users[chat_id]
        name = user_data.get('name')
        age = user_data.get('age')
        if name and age:
            random_year = random.randint(2024, 2124)  # Рандомный год с 2024 по 2124
            future_age = random_year - 2024 + age  # Возраст в будущем году
            prediction_text = f"Я вижу, вижу, что Вам, {name}, в {random_year} будет {future_age}!"
            bot.send_message(chat_id, prediction_text)
        else:
            bot.send_message(chat_id, "Пожалуйста, сначала введите /name и /age.")
    else:
        bot.send_message(chat_id, "Пожалуйста, сначала введите /name и /age.")

number_to_guess = None  # Глобальная переменная для числа, которое бот пытается угадать
guess_range = (1, 100)

@bot.message_handler(commands=['minigame'])
def minigame(message):
    global number_to_guess 
    global guess_range
    chat_id = message.chat.id
    bot.send_message(chat_id, "Загадай число от 1 до 100, а я буду пытаться угадать.")
    number_to_guess = random.randint(guess_range[0], guess_range[1])
    send_guess_keyboard(chat_id)

# Функция для отправки сообщения с кнопками
def send_guess_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=3)
    bigger_button = types.InlineKeyboardButton("Больше", callback_data="bigger")
    smaller_button = types.InlineKeyboardButton("Меньше", callback_data="smaller")
    equal_button = types.InlineKeyboardButton("Правильно", callback_data="equal")
    markup.add(bigger_button, equal_button, smaller_button)
    bot.send_message(chat_id, f"Ты загадал число "+str(number_to_guess), reply_markup=markup)

# Обработка кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    global number_to_guess  
    global guess_range
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.message:
        if call.data == "bigger":
            bot.answer_callback_query(call.id)
            guess_range = (number_to_guess + 1, guess_range[1])
            number_to_guess = random.randint(number_to_guess + 1, guess_range[1])
            send_guess_keyboard(chat_id)
        elif call.data == "smaller":
            bot.answer_callback_query(call.id)
            guess_range = (guess_range[0], number_to_guess - 1)
            number_to_guess = random.randint(guess_range[0], number_to_guess - 1)
            send_guess_keyboard(chat_id)
        elif call.data == "equal":
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "Ура! Я угадал число.")
            bot.delete_message(chat_id, message_id)


# Обработчик всех сообщений пользователя
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)

# Запуск бота
bot.polling()
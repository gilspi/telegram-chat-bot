import os
from dotenv import load_dotenv

import telebot

# токен при регистрации приложения
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

# токен бота храним в окружении
bot = telebot.TeleBot(API_TOKEN)

# название БД
NAME_BD = 'emplyees.sqlite'
# id канала, с тестированными
CHANNEL_ID = '-1001887005937'
# id администратора
ALLOWED_CHAT_IDS = [686854050, 5357408101, 967697323]  # изменить потом на id admin


# Родительский путь
BASE_FILES_PATH = os.getcwd()
# Путь к папке
TXT_FOLDER_PATH = os.path.join(BASE_FILES_PATH, 'txt_files')

# Проверяем существует ли папка, если нет, то создаем ее
if not os.path.exists(TXT_FOLDER_PATH):
    os.mkdir(TXT_FOLDER_PATH)

# Путь к файлам базы данных
COMPLETED_USERS_FILE = os.path.join(TXT_FOLDER_PATH, 'completed_users.txt')
QUESTIONS_TRAFFIC_HANDLER_FILE = os.path.join(TXT_FOLDER_PATH, 'questions_traffic_handler.txt')
QUESTIONS_MEDIA_BUYER_FILE = os.path.join(TXT_FOLDER_PATH, 'questions_media_buyer.txt')


# приветствие
GREETINGS_ADMIN = """
Привет!

Это Telegram-бот для первичной поверки кандидатов на определенную должность.

/start - приветственное сообщение
/test - ответить на вопросы
/showall - показать все вопросы
/deleteall - удалить все вопросы
/create - создать вопрос
"""

GREETINGS = """
Привет!

Это Telegram-бот для первичной поверки кандидатов на определенную должность.

/start - приветственное сообщение
*На какую вакансию вы откликаетесь?*
"""

# вопросы
QUESTIONS_TRAFFIC_HANDLER = []
QUESTIONS_MEDIA_BUYER = []

# названия команд
COMMANDS = {
    'START': '/start',
    'CREATE': '/create',
    'SHOWALL': '/showall',
    'DELETEALL': '/deleteall',
    'TEST': '/test',

}

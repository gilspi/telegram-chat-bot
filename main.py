import time
import threading

import telebot
from telebot import types

from settings import config
from settings.config import bot

from questions_utils import load_questions, save_question, delete_all_questions
from completed_users_utils import save_completed_users, load_completed_users

# Словарь для хранения ответов каждого пользователя
user_answers = {}

users = {}

completed_users = load_completed_users()  # Пользователи, прошедшие тест
config.QUESTIONS_TRAFFIC_HANDLER = load_questions('traffic-handler')
config.QUESTIONS_MEDIA_BUYER = load_questions('media-buyer')


# ВЫНЕСТИ В ОТДЕЛЬНЫЙ МОДУЛЬ
def delete_message_with_delay(user_id, message_id):
    def delete_message():
        time.sleep(10)  # Задержка в 10 секунд
        bot.delete_message(user_id, message_id)

    threading.Thread(target=delete_message).start()


def delete_message_wrapper(func):
    def wrapper(message):
        user_id = message.chat.id
        text = None
        delete_message = None
        if message.chat.type == 'supergroup':
            text = 'Я не обрабатываю команды в этом чате.' if message.text.startswith('/') else 'Это канал с отчетными данными'
            try:
                bot.delete_message(user_id, message.message_id)
                delete_message = bot.send_message(user_id, text)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка при удалении сообщения: {e}")
        elif message.chat.type == 'private':
            if message.text.startswith('/') and message.text in config.COMMANDS.values():
                func(message)
            else:
                text = 'Введена неверная команда!' if message.text not in config.COMMANDS.values() else 'Введены некорректные данные!'
                try:
                    bot.delete_message(user_id, message.message_id)
                    delete_message = bot.send_message(user_id, text)
                except telebot.apihelper.ApiTelegramException as e:
                    print(f"Ошибка при удалении сообщения: {e}")
        else:
            func(message)

        if delete_message is not None:
            delete_message_with_delay(user_id, delete_message.message_id)

    return wrapper


@bot.message_handler(commands=['start'])
@delete_message_wrapper
def main(message):
    user_id = message.chat.id

    if user_id not in completed_users:
        markup = types.InlineKeyboardMarkup()

        traffic_handler = types.InlineKeyboardButton('Обработчик трафика', callback_data='traffic-handler')
        media_buyer = types.InlineKeyboardButton('Медиа байер', callback_data='media-buyer')

        markup.add(traffic_handler, media_buyer)

        if message.from_user.id in config.ALLOWED_CHAT_IDS:
            bot.send_message(message.chat.id, config.GREETINGS_ADMIN, reply_markup=markup, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, config.GREETINGS, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, '*Тест пройден. Ожидайте, с Вами свяжется менеджер!*', parse_mode='Markdown')


# Обработчик нажатия на инлайн-кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    users[call.message.chat.id] = True
    flag = None
    if call.data == 'traffic-handler':
        flag = 'traffic-handler'
        # При запуске бота, загружаем вопросы из файла

        bot.send_message(call.message.chat.id, 'Вводите команду /test и проходи тест!')
    elif call.data == 'media-buyer':
        flag = 'media-buyer'

        bot.send_message(call.message.chat.id, 'Вводите команду /test и проходи тест!')

    users[call.message.chat.id] = flag  # Устанавливаем flag в users
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)


# Функция для отправки вопроса пользователю
def send_question(message, user_id):
    print('users[user_id]', users[user_id])
    if user_id in users:
        if users[user_id]:
            question = users[user_id][0]
            print('question', question)
            bot.send_message(user_id, question)
            bot.register_next_step_handler(message, process_answer, user_id)  # Добавляем user_id как аргумент
        else:
            send_results_to_channel(message)
            bot.send_message(user_id, "Вопросы закончились.")
    else:
        bot.send_message(user_id, "Что-то пошло не так. Попробуйте снова.")


def send_results_to_channel(message):
    user_id = message.chat.id
    results_message = f"Ответы пользователя @{message.from_user.username}:\n"

    for question, answer_data in user_answers.get(user_id, {}).items():
        results_message += f"\nВопрос: {question}\n"

        if 'photo_url' in answer_data:
            results_message += f"Фото: {answer_data['photo_url']}\n"
        elif 'document_url' in answer_data:
            results_message += f"Фото: {answer_data['document_url']}\n"
        else:
            results_message += f"Ответ: {answer_data}\n"

    # Отправляем все ответы (и фото, и текст) вместе в одном сообщении
    try:
        bot.send_message(config.CHANNEL_ID, results_message)
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

    # save_completed_users(user_id)
    user_answers.clear()
    print(users)
    print(user_answers)


# Функция для обработки ответа пользователя
def process_answer(message, user_id):
    if message.text and message.text.lower() == "стоп" or len(users.get(user_id, [])) == 0:
        bot.send_message(message.chat.id, "Вы завершили тест.")
        return

    current_question = users[user_id][0]
    users[user_id] = users[user_id][1:]  # Удаляем первый вопрос

    if message.photo:
        # Если есть изображение, то сохраняем его
        photo_file_id = message.photo[-1].file_id
        photo_info = bot.get_file(photo_file_id)
        photo_path = photo_info.file_path
        photo_url = f'https://api.telegram.org/file/bot{config.API_TOKEN}/{photo_path}'

        # Сохраняем ссылку на фото
        user_answers.setdefault(user_id, {}).setdefault(current_question, {})['photo_url'] = photo_url

    elif message.document:
        # Если есть документ, то сохраняем его
        document_file_id = message.document.file_id
        document_info = bot.get_file(document_file_id)
        document_path = document_info.file_path
        document_url = f'https://api.telegram.org/file/bot{config.API_TOKEN}/{document_path}'

        # Сохраняем ссылку на документ
        user_answers.setdefault(user_id, {}).setdefault(current_question, {})['document_url'] = document_url

    else:
        # Проверяем, есть ли уже ответ для данного вопроса
        if current_question not in user_answers.get(user_id, {}):
            user_answers.setdefault(user_id, {})[current_question] = message.text  # Сохраняем ответ

    send_question(message, user_id)


@bot.message_handler(commands=['test'])
def test(message):
    print(users)
    flag = users.get(message.chat.id)
    if users.get(message.chat.id):
        if flag == 'traffic-handler':
            if config.QUESTIONS_TRAFFIC_HANDLER:
                user_id = message.chat.id
                users[user_id] = config.QUESTIONS_TRAFFIC_HANDLER.copy()  # Копируем вопросы для данного пользователя
                send_question(message, user_id)
            else:
                bot.send_message(message.chat.id, "К сожалению, вопросов пока нет.")
        else:
            if config.QUESTIONS_MEDIA_BUYER_FILE:
                user_id = message.chat.id
                users[user_id] = config.QUESTIONS_MEDIA_BUYER.copy()  # Копируем вопросы для данного пользователя
                send_question(message, user_id)
            else:
                bot.send_message(message.chat.id, "К сожалению, вопросов пока нет.")
    else:
        bot.send_message(message.chat.id, 'Введите команду /start и выберите нужную вакансию для Вас!')


@bot.message_handler(commands=[config.COMMANDS.get('CREATE')])
def create_question(message):
    user_id = message.from_user.id
    if user_id in config.ALLOWED_CHAT_IDS:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        traffic_handler_button = types.KeyboardButton('Traffic Handler')
        media_buyer_button = types.KeyboardButton('Media Buyer')
        markup.row(traffic_handler_button, media_buyer_button)

        bot.send_message(message.chat.id, 'Выберите категорию вопроса:', reply_markup=markup)
        bot.register_next_step_handler(message, process_category)
    else:
        bot.send_message(message.chat.id, 'У вас нет разрешений использовать эту команду.')


def process_category(message):
    user_id = message.from_user.id
    category = message.text

    if category in {'Traffic Handler', 'Media Buyer'}:  # вынести в config
        if category == 'Traffic Handler':
            users[user_id] = 'traffic-handler'
        elif category == 'Media Buyer':
            users[user_id] = 'media-buyer'

        bot.send_message(user_id, 'Введите новый тестовый вопрос.')
        bot.register_next_step_handler(message, save_question, users)
    else:
        bot.send_message(message.chat.id, 'Некорректная категория. Попробуйте еще раз.')


@bot.message_handler(commands=['showall'])
def show_all_questions(message):
    user_id = message.from_user.id
    if user_id in config.ALLOWED_CHAT_IDS:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        traffic_handler_button = types.KeyboardButton('Traffic Handler')
        media_buyer_button = types.KeyboardButton('Media Buyer')
        markup.row(traffic_handler_button, media_buyer_button)

        bot.send_message(message.chat.id, 'Выберите категорию вопросов:', reply_markup=markup)
        bot.register_next_step_handler(message, process_show_questions)
    else:
        bot.send_message(message.chat.id, 'У вас нет разрешений использовать эту команду.')


def process_show_questions(message):
    category = message.text

    if category == 'Traffic Handler':
        show_questions_from_file(message, 'traffic-handler')
    elif category == 'Media Buyer':
        show_questions_from_file(message, 'media-buyer')
    else:
        bot.send_message(message.chat.id, 'Некорректная категория. Попробуйте еще раз.')


def show_questions_from_file(message, flag):
    questions = load_questions(flag)

    if questions:
        questions_str = '\n'.join([f"{i+1}. {question}" for i, question in enumerate(questions)])
        bot.send_message(message.chat.id, questions_str)
    else:
        bot.send_message(message.chat.id, 'Список вопросов пуст.')


@bot.message_handler(commands=['deleteall'])
def delete_all_questions_command(message):
    user_id = message.from_user.id
    if user_id in config.ALLOWED_CHAT_IDS:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        traffic_handler_button = types.KeyboardButton('Traffic Handler')
        media_buyer_button = types.KeyboardButton('Media Buyer')
        markup.row(traffic_handler_button, media_buyer_button)

        bot.send_message(message.chat.id, 'Выберите категорию для удаления вопросов:', reply_markup=markup)
        bot.register_next_step_handler(message, process_delete_category)
    else:
        bot.send_message(message.chat.id, 'У вас нет разрешений использовать эту команду.')


def process_delete_category(message):
    user_id = message.from_user.id
    category = message.text

    if category == 'Traffic Handler':
        flag = 'traffic-handler'
    elif category == 'Media Buyer':
        flag = 'media-buyer'
    else:
        bot.send_message(message.chat.id, 'Некорректная категория. Попробуйте еще раз.')
        return

    delete_all_questions(user_id, flag)


@bot.message_handler(func=lambda message: True)
@delete_message_wrapper
def text_handler(message):
    user_id = message.chat.id

    if message.chat.type == 'private':
        user_state = users.get(user_id, {}).get('state')
        if user_state == 'entering_question':
            save_question(message, users)
    else:
        bot.send_message(message.chat.id, 'Вы ввели некорректные данные!')


bot.enable_save_next_step_handlers(delay=10)
bot.load_next_step_handlers()

if __name__ == "__main__":
    bot.infinity_polling(none_stop=True)

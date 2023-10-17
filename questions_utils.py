"""Скрипт подгружает файл с вопросами"""
import os
from settings import config
from settings.config import bot
from settings.config import QUESTIONS_MEDIA_BUYER_FILE, QUESTIONS_TRAFFIC_HANDLER_FILE, \
    QUESTIONS_TRAFFIC_HANDLER, QUESTIONS_MEDIA_BUYER


# При запуске бота, загружаем вопросы из файла
def load_questions(flag):
    file_path = None
    if flag == 'traffic-handler':
        file_path = QUESTIONS_TRAFFIC_HANDLER_FILE
    else:
        file_path = QUESTIONS_MEDIA_BUYER_FILE

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()
            questions = [line.rstrip('\n') + '?' if not line.rstrip('\n').endswith('?') else line.rstrip('\n')
                         for line in lines]
            print(questions)
            return questions
    return []


def is_question_exists(question, flag):
    file_path = None
    if flag == 'traffic-handler':
        file_path = QUESTIONS_TRAFFIC_HANDLER_FILE
    else:
        file_path = QUESTIONS_MEDIA_BUYER_FILE

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()
            questions = [line.rstrip('\n') for line in lines]
            return question.lower() in [q.lower() for q in questions]
    return False


def save_question(message, user_data_manager):
    user_id = message.from_user.id
    user_data_manager.print_data(user_id)
    flag = user_data_manager.get_data(user_id, 'flag')

    if flag:
        if message.content_type == 'text':
            text = message.text.rstrip('\n').capitalize()
            if not is_question_exists(text, flag):
                if flag == 'traffic-handler':
                    with open(config.QUESTIONS_TRAFFIC_HANDLER_FILE, 'a') as f:
                        f.write(f"{text}?\n" if not text.endswith('?') else f"{text}\n")
                    config.QUESTIONS_TRAFFIC_HANDLER.append(text)
                else:
                    with open(config.QUESTIONS_MEDIA_BUYER_FILE, 'a') as f:
                        f.write(f"{text}?\n" if not text.endswith('?') else f"{text}\n")
                    config.QUESTIONS_MEDIA_BUYER.append(text)

                bot.send_message(message.chat.id, 'Вопрос успешно добавлен.')
            else:
                bot.send_message(message.chat.id, 'Такой вопрос уже существует.')
        else:
            bot.send_message(user_id, "Некорректный формат ввода. Введите текст вопроса.")
            bot.register_next_step_handler(message, save_question, user_data_manager)  # ВОЗМОЖНО ПОПАДАНИЕ В РЕКУРСИЮ
    else:
        bot.send_message(user_id, "Что-то пошло не так. Попробуйте снова.")


def delete_all_questions(user_id, flag):
    file_path = None
    questions_list = None

    if flag == 'traffic-handler':
        file_path = QUESTIONS_TRAFFIC_HANDLER_FILE
        questions_list = QUESTIONS_TRAFFIC_HANDLER
    else:
        file_path = QUESTIONS_MEDIA_BUYER_FILE
        questions_list = QUESTIONS_MEDIA_BUYER

    if os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write('')
        questions_list.clear()
        bot.send_message(user_id, f'Все вопросы категории {flag} успешно удалены.')
    else:
        bot.send_message(user_id, f'Список вопросов категории {flag} пуст.')

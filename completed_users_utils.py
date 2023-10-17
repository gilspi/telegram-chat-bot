"""Скрипт загружает и выгружает новых пользователей в completed_users.txt"""
import os
from settings.config import COMPLETED_USERS_FILE


def load_completed_users():
    """Проверяет создан ли такой файл. Выполняется форматирование выгруженных данных.
    Загрузка id пользователе, которые прошли тест.
    """
    if os.path.exists(COMPLETED_USERS_FILE):
        with open(COMPLETED_USERS_FILE, 'r') as f:
            lines = f.readlines()
            # Убираем символ конца строки из каждой строки
            user_ids = [int(line.rstrip('\n')) for line in lines]
            return user_ids
    else:
        with open(COMPLETED_USERS_FILE, 'w'):
            return []


def save_completed_users(user_id):
    completed_users = load_completed_users()

    if user_id not in completed_users:
        completed_users.append(user_id)

        with open(COMPLETED_USERS_FILE, 'a') as f:
            f.write(f'{user_id}\n')

        return 'Success save'
    else:
        return 'User already saved'

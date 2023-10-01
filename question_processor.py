class QuestionProcessor:

    @staticmethod
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
            user_answers.setdefault(user_id, {}).setdefault(current_question, {})['photo_url'] = photo_url

        elif message.document:
            # Если есть документ, то сохраняем его
            document_file_id = message.document.file_id
            document_info = bot.get_file(document_file_id)
            document_path = document_info.file_path
            document_url = f'https://api.telegram.org/file/bot{config.API_TOKEN}/{document_path}'
            user_answers.setdefault(user_id, {}).setdefault(current_question, {})['document_url'] = document_url

        else:
            if current_question not in user_answers.get(user_id, {}):
                user_answers.setdefault(user_id, {})[current_question] = message.text  # Сохраняем ответ

        send_question(message, user_id)

    @staticmethod
    def process_category(message):
        user_id = message.from_user.id
        category = message.text

        if category in {'Traffic Handler', 'Media Buyer'}:
            if category == 'Traffic Handler':
                users[user_id] = 'traffic-handler'
            elif category == 'Media Buyer':
                users[user_id] = 'media-buyer'

            bot.send_message(user_id, 'Введите новый тестовый вопрос.')
            bot.register_next_step_handler(message, save_question, users)
        else:
            bot.send_message(message.chat.id, 'Некорректная категория. Попробуйте еще раз.')

    @staticmethod
    def process_show_questions(message):
        category = message.text

        if category == 'Traffic Handler':
            show_questions_from_file(message, 'traffic-handler')
        elif category == 'Media Buyer':
            show_questions_from_file(message, 'media-buyer')
        else:
            bot.send_message(message.chat.id, 'Некорректная категория. Попробуйте еще раз.')

    @staticmethod
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

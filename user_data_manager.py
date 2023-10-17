class UserDataManager:
    def __init__(self):
        self._user_data = {}

    def set_data(self, user_id, key, value):
        if user_id not in self._user_data:
            self._user_data[user_id] = {}
        self._user_data[user_id][key] = value

    def get_data(self, user_id, key=None):
        if key is None:
            return self._user_data
        return self._user_data.get(user_id, {}).get(key)

    def add_data(self, user_id, key, value):
        if user_id not in self._user_data:
            self._user_data[user_id] = {}
        self._user_data[user_id].setdefault(key, []).append(value)

    def clear_data(self, user_id, key):
        if user_id in self._user_data and key in self._user_data[user_id]:
            del self._user_data[user_id][key]

    def check_user_existence(self, user_id):
        return user_id in self._user_data

    def print_data(self, user_id):
        user_data = self._user_data.get(user_id)
        if user_data:
            print(f"User ID: {user_id}")
            for key, value in user_data.items():
                print(f"{key}: {value}")
        else:
            print(f"No data found for user ID: {user_id}")

    def remove_first_question(self, user_id):
        if user_id in self._user_data and 'questions' in self._user_data[user_id]:
            questions = self._user_data[user_id]['questions']
            if questions:
                self._user_data[user_id]['questions'] = questions[1:]

    def has_questions(self, user_id):
        if len(self.get_data(user_id, 'questions')):
            return True
        return False


user_data_manager = UserDataManager()

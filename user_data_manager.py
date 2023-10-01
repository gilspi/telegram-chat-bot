class UserDataManager:
    def __init__(self):
        self.user_data = {}

    def set_data(self, user_id, key, value):
        if user_id not in self.user_data:
            self.user_data[user_id] = {}
        self.user_data[user_id][key] = value

    def get_data(self, user_id, key):
        return self.user_data.get(user_id, {}).get(key)

    def clear_data(self, user_id, key):
        if user_id in self.user_data and key in self.user_data[user_id]:
            del self.user_data[user_id][key]

    def check_user_existence(self, user_id):
        return user_id in self.user_data

    def remove_first_question(self, user_id):
        if user_id in self.user_data and 'questions' in self.user_data[user_id]:
            questions = self.user_data[user_id]['questions']
            if questions:
                self.user_data[user_id]['questions'] = questions[1:]


user_data_manager = UserDataManager()

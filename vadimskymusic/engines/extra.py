class Extra:
    def __init__(self):
        self.__storage = {}

    async def put(self, user_id, key, value):
        if user_id not in self.__storage:
            self.__storage[user_id] = {}
        self.__storage[user_id][key] = value

    async def get(self, user_id, key, delete: bool):
        value = self.__storage[user_id][key]
        if delete:
            del self.__storage[user_id][key]
        return value

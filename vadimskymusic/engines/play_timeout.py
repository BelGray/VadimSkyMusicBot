import asyncio


class PlayTimeout:

    def __init__(self, seconds: int):
        self.__timeout_tracks = {}
        self.__seconds = seconds

    @property
    def timeout_tracks(self):
        return self.__timeout_tracks

    @property
    def seconds(self):
        return self.__seconds

    async def __arrest_user(self, user_id, track_name):
        if user_id not in self.timeout_tracks:
            self.__timeout_tracks[user_id] = {}
        self.__timeout_tracks[user_id][track_name] = 1

    async def __free_user(self, user_id, track_name):
        del self.__timeout_tracks[user_id][track_name]

    async def timeout_user(self, user_id: int, track_name: str):
        await self.__arrest_user(user_id, track_name)
        await asyncio.sleep(self.seconds)
        await self.__free_user(user_id, track_name)



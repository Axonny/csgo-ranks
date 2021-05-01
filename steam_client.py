from steampy.client import SteamClient
from steampy.login import LoginExecutor

class SteamClient(SteamClient):

    def login(self, username: str, password: str, steam_guard: dict) -> None:
        self.steam_guard = steam_guard
        self.username = username
        self._password = password
        LoginExecutor(username, password, self.steam_guard['shared_secret'], self._session).login()
        self.was_login_executed = True
        self.market._set_login_executed(self.steam_guard, self._get_session_id())

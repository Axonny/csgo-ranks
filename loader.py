import json
from os import listdir


class LoaderFromFiles:
    __slots__ = {"accounts_file", "path_to_mafiles", "data"}

    def __init__(self, accounts_file: str, path_to_mafiles: str):
        self.accounts_file = accounts_file
        self.path_to_mafiles = path_to_mafiles
        self.data = None

    @property
    def result(self):
        if self.data is None:
            self.data = self._create_accounts_list()

        return self.data

    def _load_accounts(self) -> dict:
        accounts = {}
        with open(self.accounts_file, "r", encoding="utf-8") as f:
            for string in f.readlines():
                if string.strip():
                    account_name, password = string.split()
                    account_name = account_name.lower()
                    if not account_name.startswith("#"):
                        accounts[account_name] = {"password": password}
        return accounts

    def _load_ma_files(self) -> dict:
        maFiles = {}
        for file in listdir(self.path_to_mafiles):
            if file.endswith(".maFile"):
                with open(f"{self.path_to_mafiles}/{file}", "r", encoding="utf-8") as f:
                    account_data = json.load(f)
                    account_name = account_data["account_name"].lower()
                    maFiles[account_name] = {}
                    maFiles[account_name]["mobile"] = {}
                    maFiles[account_name]["mobile"]["shared_secret"] = account_data["shared_secret"]
                    maFiles[account_name]["mobile"]["identity_secret"] = account_data["identity_secret"]
                    maFiles[account_name]["mobile"]["steamid"] = account_data["Session"]["SteamID"]
        return maFiles

    def _create_accounts_list(self) -> list:
        accounts = self._load_accounts()
        maFiles = self._load_ma_files()
        for account in accounts:
            accounts[account].update(maFiles.get(account, {}))

        return accounts


if __name__ == '__main__':
    print(LoaderFromFiles('accounts_data.txt', 'maFiles').result)

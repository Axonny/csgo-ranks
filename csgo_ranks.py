import json
import re
import time
import pyperclip
from steam_client import SteamClient
from loader import LoaderFromFiles


class csgoRankParser():

    __slots__ = {'accounts_data', 're_rank', 're_exp', 'data', 'debug'}

    def __init__(self, accounts_data: dict, debug: bool):
        self.accounts_data = accounts_data
        self.re_rank = re.compile(r'CS:GO Profile Rank: (\d+)')
        self.re_exp = re.compile(r'Experience points earned towards next rank: (\d+)')
        self.data = None
        self.debug = debug

    @property
    def result(self):
        if self.data == None:
            self.data = self.get_all_ranks()

        return self.data

    def get_rank(self, name: str) -> dict:
        data = self.accounts_data[name]
        steam_client = SteamClient("gf")
        steam_client.login(name, data["password"], data["mobile"])

        session = steam_client._session
        url = f'https://steamcommunity.com/profiles/{data["mobile"]["steamid"]}/gcpd/730/'

        html = session.get(url).text
        res = {
            "rank": self.re_rank.findall(html)[0],
            "expirience": self.re_exp.findall(html)[0]
        }

        if self.debug:
            print('\t'.join([name, res['rank'], res['expirience']]))
        return res

    def get_all_ranks(self) -> dict:
        result = {}
        for name in self.accounts_data.keys():
            result[name] = self.get_rank(name)
            time.sleep(30)
        return result

    def get_beautify_str(self) -> str:
        res = []
        accounts = self.result
        print(self.result)
        for name in accounts:
            account = accounts[name]
            res.append('\t'.join([name, account['rank'], account['expirience']]))

        return '\n'.join(res)

    def save_to_file(self, filename: str) -> None:
        with open(filename, "w", encoding='utf-8') as f:
            f.write(self.get_beautify_str())

    def save_to_buffer(self) -> None:
        pyperclip.copy(self.get_beautify_str())

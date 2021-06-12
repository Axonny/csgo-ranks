import json
import re
import time
import pyperclip
from steam_client import SteamClient
from loader import LoaderFromFiles
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


class CSGORankParser:

    __slots__ = {'accounts_data', 're_rank', 're_exp', 'data', 'debug'}

    def __init__(self, accounts_data: dict, debug: bool):
        self.accounts_data = accounts_data
        self.re_rank = re.compile(r'CS:GO Profile Rank: (\d+)')
        self.re_exp = re.compile(r'Experience points earned towards next rank: (\d+)')
        self.data = None
        self.debug = debug

    @property
    def result(self):
        if self.data is None:
            self.data = self.get_all_ranks()

        return self.data

    def get_rank(self, name: str) -> dict:
        data = self.accounts_data[name]
        steam_client = SteamClient("gf")
        steam_client.login(name, data["password"], data["mobile"])

        session = steam_client._session
        url = f'https://steamcommunity.com/profiles/{data["mobile"]["steamid"]}/gcpd/730/'
        url_inv = f'https://steamcommunity.com/profiles/{data["mobile"]["steamid"]}/inventoryhistory/?app%5B%5D=730'

        html = session.get(url).text
        res = {
            "rank": self.re_rank.findall(html)[0],
            "expirience": self.re_exp.findall(html)[0],
            "drop": "",
            "case": ""
        }

        inv_history = session.get(url_inv).text
        soup = BeautifulSoup(inv_history, "html.parser")
        for row in soup.find_all("div", {"class": "tradehistoryrow"}):
            reason = row.find("div", {"class": "tradehistory_event_description"}).get_text().strip()
            date_div = row.find("div", {"class": "tradehistory_date"})
            date_text = " ".join(date_div.get_text().strip().split())
            date = datetime.strptime(date_text, "%d %b, %Y %I:%M%p")
            if reason == "Got an item drop" and res["case"] == "":
                res["case"] = date.strftime("%d.%m.%Y %H:%M")
            elif reason == "Earned a new rank and got a drop" and res["drop"] == "":
                cur_day = datetime.now().weekday()
                different_days = cur_day - 2 if cur_day >= 2 else 5 + cur_day
                wednesday = datetime.now() - timedelta(days=different_days)
                wednesday -= timedelta(hours=wednesday.hour-5)
                if wednesday <= date:
                    res["drop"] = "+"
                else:
                    res["drop"] = "-"

        if self.debug:
            print('\t'.join([name, *res.values()]))
        return res

    def get_all_ranks(self) -> dict:
        result = {}
        for name in self.accounts_data.keys():
            result[name] = self.get_rank(name)
            time.sleep(10)
        return result

    def get_beautify_str(self) -> str:
        res = []
        accounts = self.result
        for name in accounts:
            account = accounts[name]
            res.append('\t'.join(account.values()))

        return '\n'.join(res)

    def save_to_file(self, filename: str) -> None:
        with open(filename, "w", encoding='utf-8') as f:
            f.write(self.get_beautify_str())

    def save_to_buffer(self) -> None:
        pyperclip.copy(self.get_beautify_str())

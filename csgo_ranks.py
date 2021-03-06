import json
import re
import time
import pyperclip
from steam_client import SteamClient
from loader import LoaderFromFiles
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


class CSGORankParser:

    __slots__ = {'accounts_data', 're_rank', 're_exp','re_time', 'data', 'debug'}

    def __init__(self, accounts_data: dict, debug: bool):
        self.accounts_data = accounts_data
        self.re_rank = re.compile(r'CS:GO Profile Rank: (\d+)')
        self.re_exp = re.compile(r'Experience points earned towards next rank: (\d+)')
        self.re_time = re.compile(r'Logged out of CS:GO(.*)GMT')
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
        session.cookies["Steam_Language"] = "english"
        url = f'https://steamcommunity.com/profiles/{data["mobile"]["steamid"]}/gcpd/730/'
        url_inv = f'https://steamcommunity.com/profiles/{data["mobile"]["steamid"]}/inventoryhistory/?app%5B%5D=730'

        html = session.get(url).text
        last_run = datetime.utcnow() - datetime.strptime(self.re_time.findall(html)[0].strip()[9:], "%Y-%m-%d %H:%M:%S")
        res = {
            "rank": self.re_rank.findall(html)[0],
            "expirience": self.re_exp.findall(html)[0],
            "drop": "",
            "case": "",
            "time": str(last_run.days)
        }

        inv_history = session.get(url_inv).text
        soup = BeautifulSoup(inv_history, "html.parser")
        for row in soup.find_all("div", {"class": "tradehistoryrow"}):
            reason = row.find("div", {"class": "tradehistory_event_description"}).get_text().strip()
            date_div = row.find("div", {"class": "tradehistory_date"})
            date_text = " ".join(date_div.get_text().strip().split())
            date = datetime.strptime(date_text, "%d %b, %Y %I:%M%p")
            if reason == "Got an item drop" and res["case"] == "":
                date_now = datetime.utcnow() - timedelta(days=7, hours=7)
                different = self._timedelta2str(date - date_now)
                res["case"] = f"+ ({different})" if date >= date_now else "-"
            elif reason == "Earned a new rank and got a drop" and res["drop"] == "":
                cur_day = datetime.now().weekday()
                different_days = cur_day - 2 if cur_day >= 2 else 5 + cur_day
                wednesday = datetime.utcnow() - timedelta(days=different_days)
                wednesday -= timedelta(hours=wednesday.hour, minutes=wednesday.minute, seconds=wednesday.second)
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

    def _timedelta2str(self, delta: timedelta) -> str:
    	days = f"{delta.days} day{'s,' if delta.days > 1 else ',  '}"
    	_, mod = divmod(int(delta.total_seconds()), 3600 * 24)
    	hours, mod = divmod(mod, 3600)
    	minutes, seconds = divmod(mod, 60)
    	time = f"{hours:0>2}:{minutes:0>2}:{seconds:0>2}"
    	return f"{days} {time}"

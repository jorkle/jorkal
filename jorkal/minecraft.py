import os

import requests
from dotenv import load_dotenv
from mctools import QUERYClient, RCONClient

load_dotenv()


class Minecraft:
    def __init__(self, host, rcon_password):
        self.host = host
        self.rcon_password = rcon_password
        self.rcon_session = False
        self.stop_url = os.getenv("STOP_URL")
        self.start_url = os.getenv("START_URL")

    def _connect(self):
        try:
            rcon = RCONClient(self.host)
            self.rcon_session = rcon.login(self.rcon_password)
            return self.rcon_session
        except Exception as e:
            print(e)
            return False

    def start(self):
        while True:
            r = requests.get(self.start_url)
            if r.status_code == 200:
                break
            else:
                continue
        return

    def stop(self):
        while True:
            r = requests.get(self.stop_url)
            if r.status_code == 200:
                break
            else:
                continue
        return

    def get_player_count(self):
        query = QUERYClient(self.host)
        query_response = query.get_basic_stats()
        return query_response["numplayers"]

    def get_online_players(self):
        query = QUERYClient(self.host)
        query_response = query.get_full_stats()
        return query_response["players"]

    def set_time(self, time):

        rcon = RCONClient(self.host)
        self.rcon_session = rcon.login(self.rcon_password)
        if time == "day":
            self.rcon_session.command("time set day")
        if time == "night":
            self.rcon_session.command("time set night")
        return

    def set_weather(self, weather):

        rcon = RCONClient(self.host)
        self.rcon_session = rcon.login(self.rcon_password)
        if weather == "clear":
            self.rcon_session.command("weather clear")
        if weather == "rain":
            self.rcon_session.command("weather rain")
        return

    def whitelist(self, mode, username):

        rcon = RCONClient(self.host)
        self.rcon_session = rcon.login(self.rcon_password)
        if mode == "add":
            self.rcon_session.command(f"whitelist add {username}")
        if mode == "remove":
            self.rcon_session.command(f"whitelist remove {username}")
        self.rcon_session.command("whitelist reload")
        return

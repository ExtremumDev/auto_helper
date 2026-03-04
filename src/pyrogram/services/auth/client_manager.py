from typing import Dict

from pyrogram import Client



class ClientManager:

    def __init__(self):
        self.accounts: Dict[str, Client] = {}

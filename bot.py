import pyromod.listen, asyncio, sys
from pyrogram import Client
from config import API_HASH, APP_ID, TG_BOT_TOKEN



class Bot(Client):
    def __init__(self):
        super().__init__(
            "Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            bot_token=TG_BOT_TOKEN)

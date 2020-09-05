import os

from pyrogram import Client
from pyrogram.scaffold import Scaffold

from .config import config


telegram = Client(os.getenv("NETWORK_SHORT_NAME", "tmnetbot"),
                  api_id=config.get("TELEGRAM_API_ID"),
                  api_hash=config.get("TELEGRAM_API_HASH"),
                  bot_token=config.get("TELEGRAM_BOT_TOKEN"),
                  workdir=Scaffold.PARENT_DIR / '..')

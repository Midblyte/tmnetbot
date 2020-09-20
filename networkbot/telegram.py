# tmnetbot - Telegram bot
# Copyright (C) 2020 Midblyte <https://github.com/Midblyte>
#
# This file is part of tmnetbot.
#
# tmnetbot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tmnetbot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tmnetbot.  If not, see <https://www.gnu.org/licenses/>.

import os

from pyrogram import Client
from pyrogram.scaffold import Scaffold

from .config import config


telegram = Client(config.NETWORK_SHORT_NAME,
                  api_id=config.TELEGRAM_API_ID,
                  api_hash=config.TELEGRAM_API_HASH,
                  bot_token=config.TELEGRAM_BOT_TOKEN,
                  workdir=Scaffold.PARENT_DIR / '..')

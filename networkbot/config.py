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

import sys

from pyrogram.scaffold import Scaffold
import dotenv


dotenv.load(Scaffold.PARENT_DIR / '..' / ".env")

config = {}

_entries = {
    "telegram": {
        "api_id": True,
        "api_hash": True,
        "bot_token": True,
        "channel": True
    },
    "mongo": {
        "url": True
    },
    "network": {
        "short_name": False
    }
}

for section, options in _entries.items():
    for option, is_required in options.items():
        key = '_'.join([section, option]).upper()
        value = dotenv.get(key, default=None)
        if is_required and value is None:
            sys.exit(f"Environment variable not found: '{key}'")
        config[key] = value

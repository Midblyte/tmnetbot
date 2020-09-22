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
import sys
from collections import namedtuple

from pyrogram.scaffold import Scaffold
import dotenv


dotenv.load(Scaffold.PARENT_DIR / '..' / ".env")

_required = ["TELEGRAM_API_ID", "TELEGRAM_API_HASH", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHANNEL", "MONGO_URL"]

_optional = {"NETWORK_SHORT_NAME": "tmnetbot", "CLI_LOCALE": "en_US"}

Config = namedtuple("Config", _required + list(_optional), defaults=_optional.values())


try:
    config = Config(*[dotenv.get(k) for k in _required], **{k: dotenv.get(k) or _optional[k] for k in _optional})
except TypeError as err:
    print(err, file=sys.stderr)

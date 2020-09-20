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

from pyrogram import idle

from . import mongo, periodic_task, config
from .internationalization import translator
from .mongo import users
from .telegram import telegram


_ = translator("cli", locale=config.CLI_LOCALE)


def main():
    mongo.init()
    telegram.start()
    periodic_task.start()
    print(_("bot_on"))

    if users.count_documents({"admin": True}) == 0:
        print(_("get_adminship"))

    idle()
    print(_("bot_off"), end="\n\n")
    telegram.stop()

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

from pyrogram import idle

from . import mongo, periodic_task
from .mongo import admins
from .telegram import telegram


def main():
    mongo.init()
    telegram.start()
    periodic_task.start()
    print("Bot on")

    if admins.estimated_document_count() == 0:
        print("[!] Usa /makemeadmin per diventare admin senza intervenire manualmente")
        print("[!] dal database. Funziona solamente quando non è rilevato alcun admin.")

    idle()
    print("Il bot verrà fermato.\n")
    telegram.stop()

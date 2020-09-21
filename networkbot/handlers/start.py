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

from html import escape

from pyrogram import filters
from pyrogram.types import Message

from ..internationalization import translator
from ..mongo import users
from ..telegram import telegram


_ = translator("start")


@telegram.on_message(filters.private & filters.command("start"))
async def start(__, message: Message):
    await message.reply_text(_("info", locale=message.from_user.language_code,
                               first_name=escape(message.from_user.first_name),
                               mention=message.from_user.mention))

    users.update_one({"user_id": message.from_user.id}, {"user_id": message.from_user.id,
                                                         "name": message.from_user.first_name,
                                                         "notifications": True,
                                                         "admin": False}, upsert=True)

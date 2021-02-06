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

from pyrogram import filters, Client
from pyrogram.errors import RPCError
from pyrogram.types import Message, User

from .. import filters as custom_filters
from ..internationalization import translator
from ..mongo import users
from ..telegram import telegram


_ = translator("declassify")


@telegram.on_message(filters.private & filters.command(["declassa", "declassify"]) & custom_filters.is_admin)
async def declassify(client: Client, message: Message):
    if ' ' not in message.text:
        return await message.reply_text(_("usage", locale=getattr(message.from_user, "language_code", None)))

    user_as_text = message.text.split(' ')[1]

    try:
        admin: User = await client.get_users(user_as_text)
    except RPCError:
        return await message.reply_text(_("not_an_user", locale=getattr(message.from_user, "language_code", None)))

    if users.find_one_and_delete({"admin": True, "user_id": admin.id}) is None:
        await message.reply_text(_("unlisted_admin", locale=getattr(message.from_user, "language_code", None)))
    else:
        await message.reply_text(_("successfully_removed", locale=getattr(message.from_user, "language_code", None),
                                   mention=admin.mention, first_name=escape(admin.first_name), id=admin.id))

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

from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.errors import RPCError

from .. import filters as custom_filters
from ..internationalization import translator
from ..mongo import users
from ..telegram import telegram


_ = translator("promote")


@telegram.on_message(filters.private & filters.command(["promuovi", "promote"]) & custom_filters.is_admin)
async def promote(client: Client, message: Message):
    if ' ' not in message.text:
        return await message.reply_text(_("usage", locale=message.from_user.language_code))

    user_as_text = message.text.split(' ')[1]

    try:
        admin = await client.get_users(user_as_text)
    except RPCError:
        return await message.reply_text(_("not_an_user", locale=message.from_user.language_code))

    if users.find_one({"user_id": admin.id, "admin": True}):
        return await message.reply_text(_("already_in_list", locale=message.from_user.language_code))

    users.insert_one({"user_id": admin.id, "name": admin.first_name, "admin": True})
    await message.reply_text(_("successfully_promoted", locale=message.from_user.language_code,
                               mention=admin.mention, first_name=admin.first_name, id=admin.id))

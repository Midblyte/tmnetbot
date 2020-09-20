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
from typing import Union, Iterable

from pyrogram import filters, Client
from pyrogram.errors import RPCError
from pyrogram.methods.chats.get_chat_members import Filters
from pyrogram.types import Message, Chat, ChatPreview, ChatMember

from .. import filters as custom_filters
from ..internationalization import translator
from ..mongo import channels
from ..telegram import telegram


_ = translator("add_channel")


@telegram.on_message(filters.private & filters.text & filters.command(["add", "aggiungi", "inserisci"]) &
                     custom_filters.is_admin)
async def add_channel(client: Client, message: Message):
    if ' ' not in message.text:
        return await message.reply_text(_("usage", locale=message.from_user.language_code))

    channel_as_text = message.text.split(' ')[1]

    try:
        channel: Union[Chat, ChatPreview] = await client.get_chat(channel_as_text)
    except RPCError:
        return await message.reply_text(_("unexisting_channel", locale=message.from_user.language_code))

    if channel.type != "channel":
        return await message.reply_text(_("not_a_channel", locale=message.from_user.language_code))

    try:
        channel_admins: Iterable[ChatMember] = filter(lambda m: not (m.user.is_deleted or m.user.is_bot),
                                                      await channel.get_members(filter=Filters.ADMINISTRATORS))
    except RPCError:
        return await message.reply_text(_("not_an_admin", locale=message.from_user.language_code))

    if channels.find_one({"channel_id": channel.id}):
        return await message.reply_text(_("already_in_list", locale=message.from_user.language_code))

    channels.insert_one({"channel_id": channel.id,
                         "name": channel.title,
                         "last_send": None,
                         "delta": None,
                         "administrators": list(map(lambda a: a.user.id, channel_admins)),
                         "scheduling": {
                             "in_queue": False,
                             "message_id": None,
                             "time_from": None,
                             "time_to": None
                         }})

    await message.reply_text(_("successfully_added", locale=message.from_user.language_code,
                               name=escape(channel.title), id=channel.id))

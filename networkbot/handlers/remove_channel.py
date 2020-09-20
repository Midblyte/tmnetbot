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
from pyrogram.errors import RPCError
from pyrogram.types import Message, Chat

from .. import filters as custom_filters
from ..internationalization import translator
from ..mongo import channels
from ..telegram import telegram


_ = translator("remove_channel")


@telegram.on_message(filters.private & filters.text & filters.command(["remove", "rm", "rimuovi"]) &
                     custom_filters.is_admin)
async def remove_channel(client: Client, message: Message):
    if ' ' not in message.text:
        return await message.reply_text(_("usage", locale=message.from_user.language_code))

    channel_as_text = message.text.split(' ')[1]

    try:
        channel: Chat = await client.get_chat(channel_as_text)
    except RPCError:
        return await message.reply_text(_("unlisted_channel", locale=message.from_user.language_code))

    if channel.type != "channel":
        return await message.reply_text(_("not_a_channel", locale=message.from_user.language_code))

    if channels.find_one_and_delete({"channel_id": channel.id}) is None:
        await message.reply_text(_("unlisted_channel", locale=message.from_user.language_code))
    else:
        await message.reply_text(_("successfully_removed", locale=message.from_user.language_code, name=channel.title,
                                   id=channel.id))

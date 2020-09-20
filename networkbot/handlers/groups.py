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

from pyrogram import filters
from pyrogram.types import Message

from ..internationalization import translator
from ..telegram import telegram


_ = translator("groups")


@telegram.on_message((filters.group_chat_created | filters.new_chat_members) & filters.group)
async def added_in_a_group(__, message: Message):
    await message.reply_text(_("channels_only", locale=message.from_user.language_code))

    await message.chat.leave()

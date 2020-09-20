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
from pyrogram.types import Message, Update, CallbackQuery

from .mongo import users


async def is_admin_filter(_, __, update: Update):
    return bool(isinstance(update, Message) and not update.from_user or users.find_one({"admin": True,
                                                                                        "user_id": update.chat.id}))

is_admin = filters.create(is_admin_filter)


async def no_admins_filter(_, __, update: Update):
    return bool(isinstance(update, Message) and users.count_documents({"admin": True}) == 0)

no_admins = filters.create(no_admins_filter)


async def arguments(*args, separator='_', method='startswith'):
    async def func(flt, __, update: Update):
        if not isinstance(update, CallbackQuery):
            return False

        joined_arguments = flt.separator.join(flt.arguments)

        return (method == 'startswith' and update.data.startswith(joined_arguments)) or \
            (method == 'equals' and update.data == joined_arguments) or \
            (method == 'endswith' and update.data.endswith(joined_arguments))

    return filters.create(
        func,
        arguments=args,
        separator=separator
    )

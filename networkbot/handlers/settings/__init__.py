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
from pyrogram.types import Message, InlineKeyboardMarkup as Keyboard, InlineKeyboardButton as Button, CallbackQuery, \
    User

from ...internationalization import translator
from ...mongo import users
from ...telegram import telegram
from ... import filters as custom_filters
from . import (
    time_range,
    channels_delta,
    network_delta,
    notifications
)


_, _g, _b = translator("settings"), translator("general"), translator("settings", "buttons")


@telegram.on_message(filters.private & filters.command(["settings", "impostazioni"]))
async def settings(__, message: Message):
    sent_message = await message.reply_text(_g("loading", locale=message.from_user.language_code))

    await _menu(sent_message, message.from_user)


@telegram.on_callback_query(custom_filters.arguments("settings", "initial"))
async def settings_cq(__, callback_query: CallbackQuery):
    await callback_query.answer()

    await _menu(callback_query.message, callback_query.from_user)


async def _menu(message: Message, user: User):
    locale = user.language_code

    keyboard = Keyboard([
        [Button(_b('notifications', locale=locale), 'settings_notifications_initial')]
    ])

    if users.find_one({"admin": True, "user_id": message.chat.id}):
        keyboard.inline_keyboard.extend([
            [Button(_b("time_range", locale=locale), 'settings_time_range_initial')],
            [Button(_b("network_delta", locale=locale), 'settings_network_delta_initial')],
            [Button(_b("channels_delta", locale=locale), 'settings_channels_delta_initial')]
        ])

    await message.edit_text(_("info", locale=locale), reply_markup=keyboard)

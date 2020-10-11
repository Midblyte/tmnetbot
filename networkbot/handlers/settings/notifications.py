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

from pyrogram.types import CallbackQuery, Message, User, InlineKeyboardMarkup as Keyboard, \
    InlineKeyboardButton as Button

from ... import filters as custom_filters
from ...internationalization import translator
from ...mongo import users
from ...telegram import telegram
from ...utils.general import extract_args, args_joiner


_PREFIX = "settings", "notifications"

_BACK = "settings", "initial"

_, _g, _e = translator(*_PREFIX), translator("general"), translator("emojis")


@telegram.on_callback_query(custom_filters.arguments(*_PREFIX, "initial"))
async def initial(__, callback_query: CallbackQuery):
    await callback_query.answer()

    await _menu(callback_query.message, callback_query.from_user)


@telegram.on_callback_query(custom_filters.arguments(*_PREFIX, "set"))
async def _set(__, callback_query: CallbackQuery):
    key, value = extract_args(callback_query.data, 2)

    users.find_one_and_update({"user_id": callback_query.from_user.id},
                              {"$set": {f"notifications.{key}": value == "True"}})

    await _menu(callback_query.message, callback_query.from_user)


async def _menu(message: Message, user: User):
    locale = user.language_code

    notifications = users.find_one({"user_id": user.id}, projection=["notifications"]).get("notifications")

    keyboard = Keyboard([])

    for key, value in notifications.items():
        keyboard.inline_keyboard.extend([[Button(
            _(key, locale=locale, emoji=_e(("on" if value else "off"), locale=locale)),
            args_joiner(*_PREFIX, "set", key, not value))]])

    keyboard.inline_keyboard.extend([[Button(_g("back"), args_joiner(*_BACK))]])

    await message.edit_text(_("info", locale=locale), reply_markup=keyboard)

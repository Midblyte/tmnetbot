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
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup as Keyboard, InlineKeyboardButton as Button, \
    User

from .. import filters as custom_filters
from ..internationalization import translator
from ..mongo import channels
from ..telegram import telegram
from ..utils.channels import format_channel_info
from ..utils.documents import get_documents_range, format_documents_list
from ..utils.general import extract_args, args_joiner
from ..utils.users import notify


_PREFIX = "info",

_, _n, _g = translator(*_PREFIX), translator("settings", "notifications"), translator("general")


@telegram.on_message(filters.private & filters.command("info"))
def info(__, message: Message):
    locale = getattr(message.from_user, "language_code", None)

    count = channels.count_documents({"administrators": {"$in": [message.from_user.id]}})

    if count == 0:
        return message.reply_text(_("not_an_admin", locale=locale))

    _menu(message.reply_text(_("loading_channels", locale=locale)), message.from_user)


@telegram.on_callback_query(custom_filters.arguments(*_PREFIX, "nav"))
def get_channels_info_page(_, callback_query: CallbackQuery):
    callback_query.answer()

    offset, = extract_args(callback_query.data, 1, int)

    _menu(callback_query.message, callback_query.from_user, offset)


@telegram.on_callback_query(custom_filters.arguments(*_PREFIX, "rm"))
def get_channels_info_rm(_, callback_query: CallbackQuery):
    callback_query.answer()

    channel_id, offset = extract_args(callback_query.data, 2, int)

    channels.find_one_and_update({"channel_id": channel_id, "administrators": {"$in": [callback_query.from_user.id]}},
                                 {"$set": {"scheduling": {"in_queue": False}}})

    notify("scheduling_cancelled", channel_id=channel_id, exception=callback_query.from_user.id)

    _menu(callback_query.message, callback_query.from_user, offset)


def _menu(message: Message, user: User, offset=0):
    locale = user.language_code

    documents, keyboard = get_documents_range(channels, offset, filters={"administrators": {"$in": [user.id]}},
                                              nav=lambda c, o: f"{c}_nav_{o}")

    if not keyboard:
        keyboard = Keyboard([])

    for d in documents:
        if d.get('scheduling').get('in_queue') is True:
            name, channel_id = [d.get(k) for k in ("name", "channel_id")]

            keyboard.inline_keyboard.append([Button(f"❌ {name}", args_joiner(*_PREFIX, "rm", channel_id, offset))])

    if len(keyboard.inline_keyboard) == 0:
        keyboard = None

    fmt_channels = format_documents_list(documents.rewind(),
                                         lambda c: format_channel_info(c["channel_id"], locale=locale))

    message.edit_text(_("channels_list", locale=telegram.get_users(user.id).language_code, channels=fmt_channels),
                      reply_markup=keyboard)

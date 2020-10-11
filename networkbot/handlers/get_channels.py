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
from pyrogram.methods.chats.get_chat_members import Filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup as Keyboard, InlineKeyboardButton as Button, \
    User

from .. import filters as custom_filters
from ..internationalization import translator
from ..mongo import channels
from ..telegram import telegram
from ..utils.arrays import chunk
from ..utils.channels import format_channel_info
from ..utils.documents import get_documents_range, format_documents_list
from ..utils.general import extract_args, args_joiner
from ..utils.keyboards import dummy_btn


_PREFIX = "get_channels",

_, _g, _s = translator(*_PREFIX), translator("general"), translator("schedule")


@telegram.on_message(filters.private & filters.command(["channels", "canali"]) & custom_filters.is_admin)
def get_channels(__, message: Message):
    locale = message.from_user.language_code

    if channels.estimated_document_count() == 0:
        return message.reply_text(_("none_in_list", locale=locale))

    _menu(message.reply_text(_("loading_channels", locale=locale)), message.from_user)


@telegram.on_callback_query(custom_filters.arguments(*_PREFIX, "nav"))
def get_channels_page(__, callback_query: CallbackQuery):
    callback_query.answer()

    offset, = extract_args(callback_query.data, 1, int)

    _menu(callback_query.message, callback_query.from_user, offset)


@telegram.on_callback_query(custom_filters.arguments(*_PREFIX, "info"))
def get_channel_info(client: Client, callback_query: CallbackQuery):
    callback_query.answer()

    locale = callback_query.from_user.language_code

    channel_id, back_offset, can_update_admins = extract_args(callback_query.data, 3, int)

    if not bool(can_update_admins):
        administrators = filter(lambda member: not (member.user.is_deleted or member.user.is_bot),
                                client.get_chat_members(channel_id, filter=Filters.ADMINISTRATORS))

        channels.find_one_and_update({"channel_id": channel_id},
                                     {"$set": {"administrators": list(map(lambda m: m.user.id, administrators))}})

    callback_query.message.edit_text(format_channel_info(channel_id, locale, True), reply_markup=Keyboard([
        [Button(_("update_admins", locale=locale), args_joiner(*_PREFIX, 'info', channel_id, back_offset, 0)) if
            can_update_admins else dummy_btn(_("admins_list_updated", locale=locale))],
        [Button('« '+_g("back", locale=locale), args_joiner(*_PREFIX, 'nav', back_offset))]
    ]))


def _menu(message: Message, user: User, offset=0):
    locale = user.language_code

    documents, keyboard = get_documents_range(channels, offset)

    if not keyboard:
        keyboard = Keyboard([])

    keyboard.inline_keyboard.extend(chunk([Button(d.get("name"), args_joiner(*_PREFIX, 'info', d.get('channel_id'),
                                                                             offset, 1)) for d in documents], 2))

    fmt_channels = format_documents_list(documents.rewind(),
                                         lambda c: format_channel_info(c["channel_id"], locale=locale))

    message.edit_text(_("channels_list", locale=locale, channels=fmt_channels), reply_markup=keyboard)

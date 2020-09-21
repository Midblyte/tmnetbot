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

import functools
from datetime import timedelta
from typing import Dict

from pyrogram import filters, Client
from pyrogram.methods.chats.get_chat_members import Filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup as Keyboard

from .. import filters as custom_filters
from ..internationalization import translator
from ..utils.documents import get_documents_range, format_documents_list
from ..utils.arrays import chunk
from ..utils.channels import can_send_icon
from ..mongo import channels, options
from ..telegram import telegram
from ..utils.keyboards import custom_btn, dummy_btn
from ..utils.time import fmt_time


_ = translator("get_channels")

_PREFIX = "channels"

_path = functools.partial(custom_filters.arguments, _PREFIX)


@telegram.on_message(filters.private & filters.command(["channels", "canali"]) & custom_filters.is_admin)
async def get_channels(_, message: Message):
    if channels.estimated_document_count() == 0:
        return await message.reply_text(_("none_in_list", locale=message.from_user.language_code))

    await _navigate(await message.reply_text(_("loading_channels", locale=message.from_user.language_code)))


@telegram.on_callback_query(_path('nav'))
async def get_channels_page(_, callback_query: CallbackQuery):
    await callback_query.answer()

    offset = int(callback_query.data.rsplit('_', 1)[1])

    await _navigate(callback_query.message, offset)


@telegram.on_callback_query(_path('info'))
async def get_channel_info(client: Client, callback_query: CallbackQuery):
    await callback_query.answer()

    channel_id, back_offset, can_update_admins = map(int, callback_query.data.rsplit('_', 3)[1:])

    channel = channels.find_one({"channel_id": channel_id})

    if not bool(can_update_admins):
        administrators = filter(lambda member: not (member.user.is_deleted or member.user.is_bot),
                                await client.get_chat_members(channel_id, filter=Filters.ADMINISTRATORS))

        channels.find_one_and_update({"channel_id": channel_id},
                                     {"$set": {"administrators": list(map(lambda m: m.user.id, administrators))}})

    await callback_query.message.edit_text(_format_channel_info(channel, True), reply_markup=Keyboard([
        [custom_btn(_("update_admins", locale=callback_query.from_user.language_code),
                    _PREFIX, ['info', channel_id, back_offset, 0]) if can_update_admins else
         dummy_btn(_("admins_list_updated", locale=callback_query.from_user.language_code))],
        [custom_btn('« '+_("go_back", locale=callback_query.from_user.language_code), _PREFIX, ['nav', back_offset])]
    ]))


async def _navigate(message: Message, offset=0):
    documents, keyboard = get_documents_range(channels, offset)

    if not keyboard:
        keyboard = Keyboard([])

    keyboard.inline_keyboard.extend([*map(list, chunk((
            custom_btn(d.get("name"), _PREFIX, ['info', d.get('channel_id'), offset, 1]) for d in documents), 2))])

    fmt_channels = format_documents_list(documents.rewind(), _format_channel_info)

    await message.edit_text(_("channels_list", locale=message.from_user.language_code, channels=fmt_channels),
                            reply_markup=keyboard)


def _format_channel_info(channel: Dict, detailed=False) -> str:
    name = channel.get('name')
    channel_id = channel.get('channel_id')
    last_send = channel.get('last_send')
    channel_delta = channel.get('delta')
    delta = channel_delta or options("channels_delta")
    in_queue = channel.get('scheduling').get('in_queue')
    icon = can_send_icon(last_send, delta, in_queue)
    generation_time = fmt_time(channel.get('_id').generation_time)
    last_send_time = fmt_time(last_send)

    text = f"""\
{icon} {name}
Ultimo invio » {last_send_time}"""

    if detailed:
        text = f"""\
{icon} {name} [ID {channel_id}]
Ultimo invio » {last_send_time}
Aggiunto il » {generation_time}
"""

        if icon == '🔇':
            text += f"\nProssimo invio dal: {fmt_time(last_send + timedelta(seconds=delta))}"

        if channel_delta is not None:
            text += f"\nDistanziamento personalizzato: {channel_delta} secondi"

    return text

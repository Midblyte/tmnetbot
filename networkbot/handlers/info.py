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
from datetime import timedelta
from typing import Dict, Callable

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup as Keyboard, CallbackQuery

from ..utils.channels import can_send_icon
from ..utils.documents import get_documents_range, format_documents_list
from ..mongo import channels, options
from ..telegram import telegram
from ..utils.keyboards import custom_btn
from ..utils.time import fmt_time


_PREFIX = channels.name

not_an_admin = "\
Non sei admin di alcun canale."

admin_of_these_channels = "\
<b>Canali di cui sei admin</b>:\n\n{channels}"

loading_channels = "\
Caricamento canali di cui sei amministratore..."

channels_admin_filter: Callable[[int], Dict] = lambda uid: {"administrators": {"$in": [uid]}}


@telegram.on_message(filters.private & filters.command(["info"]))
async def info(_, message: Message):
    collection_filter: Dict = channels_admin_filter(message.from_user.id)
    count = channels.count_documents(collection_filter)

    if count == 0:
        return await message.reply_text(not_an_admin)

    await _navigate(await message.reply_text(loading_channels), message.from_user.id)


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith(f"{_PREFIX}_admins_nav_")))
async def get_channels_info_page(_, callback_query: CallbackQuery):
    user_id, offset = map(int, callback_query.data.rsplit('_', 2)[1:])

    await callback_query.answer()

    await _navigate(callback_query.message, user_id, offset)


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith(f"{_PREFIX}_rm_")))
async def get_channels_info_page(_, callback_query: CallbackQuery):
    user_id, channel_id, offset = map(int, callback_query.data.rsplit('_', 3)[1:])

    channels.find_one_and_update({"channel_id": channel_id, **channels_admin_filter(user_id)},
                                 {"$set": {"scheduling": {"in_queue": False}}})

    await callback_query.answer()

    await _navigate(callback_query.message, user_id, offset)


async def _navigate(message: Message, user_id: int, offset=0):
    documents, keyboard = get_documents_range(channels, offset, filters=channels_admin_filter(user_id),
                                              nav=lambda c, o: f"{c}_admins_nav_{user_id}_{o}")

    if not keyboard:
        keyboard = Keyboard([])

    for d in documents:
        if d.get('scheduling').get('in_queue') is True:
            keyboard.inline_keyboard.append([custom_btn(d.get("name"), _PREFIX,
                                                        ["rm", user_id, d.get("channel_id"), offset])])

    if len(keyboard.inline_keyboard) == 0:
        keyboard = None

    fmt_channels = format_documents_list(documents.rewind(), _format_channel_info)

    await message.edit_text(admin_of_these_channels.format(channels=fmt_channels), reply_markup=keyboard)


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

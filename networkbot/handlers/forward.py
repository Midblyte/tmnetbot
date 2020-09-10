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

from datetime import datetime, timedelta
from typing import Optional, List, Dict

from pyrogram import filters
from pyrogram.errors import RPCError
from pyrogram.methods.chats.get_chat_members import Filters
from pyrogram.types import Message, ChatMember, CallbackQuery, InlineKeyboardMarkup as Keyboard

from ..utils.time import fmt_time, fmt_mins
from ..mongo import channels, options
from ..telegram import telegram
from ..utils.keyboards import select_double_time_keyboard, from_text, to_text, select_double_time_header, confirm_btn

_PREFIX = "forward"

not_a_channel = "\
Devi inoltrare da un canale!"

im_not_an_admin = "\
Non sono admin di quel canale!"

youre_not_an_admin = "\
Non sei admin di quel canale!"

not_part_of_the_network = "\
Il canale non fa parte del network!"

not_allowed_until = "\
Non puoi inoltrare altro. Ti sarà permesso di inviare altri messaggi in data {}"

message_sent = "\
Messaggio inviato!"

go_to_message = "\
Vai al messaggio"

already_in_queue = "\
Un messaggio da questo canale è già in attesa per l'invio"

loading = "Caricamento..."


select_time_range = f"""\
Seleziona la fascia oraria in cui desideri che il messaggio sia inviato

Fascia oraria consentita: {{general_start}} - {{general_end}}

Hai impostato:
{from_text}: {{start}}
{to_text}: {{end}}"""


@telegram.on_message(filters.private & filters.forwarded)
async def forward(_, message: Message):
    tg_channel = message.forward_from_chat

    if not tg_channel or tg_channel.type != "channel":
        return await message.reply_text(not_a_channel)

    doc_channel: Optional[Dict] = channels.find_one({"channel_id": tg_channel.id})

    if doc_channel is None:
        return await message.reply_text(not_part_of_the_network)

    try:
        channel_admins: List[ChatMember] = await tg_channel.get_members(filter=Filters.ADMINISTRATORS)
    except RPCError:
        return await message.reply_text(im_not_an_admin)

    if message.from_user.id not in map(lambda a: a.user.id, channel_admins):
        return await message.reply_text(youre_not_an_admin)

    last_send: datetime = doc_channel.get("last_send") or datetime.min

    delta: int = doc_channel.get("delta") or options("channels_delta")

    diff: timedelta = datetime.utcnow() - last_send

    if diff.total_seconds() < delta:
        return await message.reply_text(not_allowed_until.format(fmt_time(last_send + timedelta(seconds=delta))))

    if doc_channel.get("scheduling").get("in_queue"):
        return await message.reply_text(already_in_queue)

    sent_message, start, end = await message.reply_text(loading), options("time_range_start"), options("time_range_end")

    channel_id, msg_id = tg_channel.id, message.forward_from_message_id

    time_keyboard = select_double_time_keyboard(_PREFIX, start, end, ['set', channel_id, msg_id])

    fmt_text = select_time_range.format(**{k: fmt_mins(v) for k, v in
                                           {"start": start, "end": end, "general_start": start, "general_end": end}
                                           .items()})

    await sent_message.edit_text(fmt_text, reply_markup=Keyboard([
        select_double_time_header(),
        *time_keyboard,
        [confirm_btn(_PREFIX, ['confirm', channel_id, msg_id, start, end])]
    ]))


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith(f"{_PREFIX}_set_")))
async def select_forward_time(_, callback_query: CallbackQuery):
    await callback_query.answer()

    channel_id, msg_id, start, end = map(int, callback_query.data.rsplit('_', 4)[1:])

    time_keyboard = select_double_time_keyboard(_PREFIX, start, end, ['set', channel_id, msg_id])

    fmt_text = select_time_range.format(general_start=options("time_range_start"),
                                        general_end=options("time_range_end"), start=fmt_mins(start), end=fmt_mins(end))

    await callback_query.message.edit_text(fmt_text, reply_markup=Keyboard([
        select_double_time_header(),
        *time_keyboard,
        [confirm_btn(_PREFIX, ['confirm', channel_id, msg_id, start, end])]
    ]))


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith(f"{_PREFIX}_confirm_")))
async def confirm_forward_time(_, callback_query: CallbackQuery):
    await callback_query.answer()

    channel_id, msg_id, start, end = map(int, callback_query.data.rsplit('_', 4)[1:])

    if channels.find_one_and_update({"channel_id": channel_id, "scheduling.in_queue": False}, {"$set": {"scheduling": {
            "in_queue": True, "message_id": msg_id, "time_from": start, "time_to": end}}}) is None:
        return await callback_query.message.edit_text(already_in_queue)

    await callback_query.message.edit_text("Ok")

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
from typing import Optional, List, Dict, Tuple

from pyrogram import filters
from pyrogram.errors import RPCError
from pyrogram.methods.chats.get_chat_members import Filters
from pyrogram.types import Message, ChatMember, InlineKeyboardMarkup as Keyboard, InlineKeyboardButton as Button,\
    CallbackQuery

from ..helpers import fmt_time, dummy_btn, chunk, minutes_in_a_day, localize_minutes
from ..mongo import channels, options
from ..telegram import telegram


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

from_text = "Da"

to_text = "A"

select_time_range = f"""\
Seleziona la fascia oraria in cui desideri che il messaggio sia inviato

Hai impostato:
{from_text}: {{start}}
{to_text}: {{end}}"""

confirm_text = "Conferma"


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

    sent_message: Message = await message.reply_text("Loading...")

    await _select_time(sent_message, tg_channel.id, message.forward_from_message_id, options("time_range_start"),
                       options("time_range_end"))


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith("forward_set_")))
async def select_forward_time(_, callback_query: CallbackQuery):
    channel_id, msg_id, start, end = map(int, callback_query.data.rsplit('_', 4)[1:])

    await callback_query.answer()

    await _select_time(callback_query.message, channel_id, msg_id, start, end)


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith("forward_confirm_")))
async def confirm_forward_time(_, callback_query: CallbackQuery):
    channel_id, msg_id, start, end = map(int, callback_query.data.rsplit('_', 4)[1:])

    await callback_query.answer()

    if channels.find_one_and_update({"channel_id": channel_id, "scheduling.in_queue": False}, {"$set":
            {"scheduling": {"in_queue": True, "message_id": msg_id, "time_from": start, "time_to": end}}}) is None:
        return await callback_query.message.edit_text("Spiacente, un messaggio è già in coda per l'invio.")

    await callback_query.message.edit_text("Ok")


async def _select_time(message: Message, channel_id: int, msg_id: int, start: int, end: int):
    buttons, modes = (('1m', 1), ('15m', 15), ('1h', 60), ('4h', 240)),  (('+', +1), ('-', -1))

    mid_keyboard = []
    for prefix, sign in modes:
        for row_buttons_info in chunk(buttons, 2):
            mid_keyboard.append(_fwd_row(prefix, sign, row_buttons_info, channel_id, msg_id, start, end))

    await message.edit_text(select_time_range.format(start=_fmt_mins(start), end=_fmt_mins(end)), reply_markup=Keyboard(
        [[dummy_btn(from_text), dummy_btn(to_text)],
         *mid_keyboard,
         [_fwd_btn(confirm_text, channel_id, msg_id, start, end, "confirm")]]
    ))


def _fwd_btn(text: str, channel_id: int, msg_id: int, start: int, end: int, mode="set") -> Button:
    return Button(text, f"forward_{mode}_{channel_id}_{msg_id}_{start % minutes_in_a_day}_{end % minutes_in_a_day}")


def _fwd_row(prefix: str, sign: int, row_buttons_info: List[Tuple[str, int]], channel_id: int, msg_id: int, start: int,
             end: int) -> List[Button]:
    row_of_buttons: List[Button] = []

    for lf, rf in (1, 0), (0, 1):
        for label, value in row_buttons_info:
            row_of_buttons.append(
                _fwd_btn(f"{prefix}{label}", channel_id, msg_id, start + lf * sign * value, end + rf * sign * value))

    return row_of_buttons


def _fmt_mins(minutes: int, transform_function=localize_minutes) -> str:
    if transform_function is not None:
        minutes = transform_function(minutes)

    return '{:02}:{:02}'.format(minutes // 60, minutes % 60)

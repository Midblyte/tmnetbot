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
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from pyrogram import filters
from pyrogram.errors import RPCError
from pyrogram.methods.chats.get_chat_members import Filters
from pyrogram.types import Message, ChatMember, CallbackQuery, InlineKeyboardMarkup as Keyboard

from .. import filters as custom_filters
from ..internationalization import translator
from ..utils.time import fmt_time, fmt_mins
from ..utils.keyboards import select_double_time_keyboard, select_double_time_header, confirm_btn
from ..mongo import channels, options
from ..telegram import telegram


_PREFIX = "forward"

_, _g = translator(_PREFIX), translator("general"),

_path = functools.partial(custom_filters.arguments, _PREFIX)


@telegram.on_message(filters.private & filters.forwarded)
async def forward(_, message: Message):
    tg_channel = message.forward_from_chat

    if not tg_channel or tg_channel.type != "channel":
        return await message.reply_text(_("not_a_channel", locale=message.from_user.language_code))

    doc_channel: Optional[Dict] = channels.find_one({"channel_id": tg_channel.id})

    if doc_channel is None:
        return await message.reply_text(_("not_part_of_the_network", locale=message.from_user.language_code))

    try:
        channel_admins: List[ChatMember] = await tg_channel.get_members(filter=Filters.ADMINISTRATORS)
    except RPCError:
        return await message.reply_text(_("im_not_an_admin", locale=message.from_user.language_code))

    if message.from_user.id not in map(lambda a: a.user.id, channel_admins):
        return await message.reply_text(_("youre_not_an_admin", locale=message.from_user.language_code))

    last_send: datetime = doc_channel.get("last_send") or datetime.min

    delta: int = doc_channel.get("delta") or options("channels_delta")

    diff: timedelta = datetime.utcnow() - last_send

    if diff.total_seconds() < delta:
        return await message.reply_text(_("not_allowed_until", locale=message.from_user.language_code,
                                          date=fmt_time(last_send + timedelta(seconds=delta))))

    if doc_channel.get("scheduling").get("in_queue"):
        return await message.reply_text(_("already_in_queue", locale=message.from_user.language_code))

    sent_message = await message.reply_text(_g("loading", locale=message.from_user.language_code))
    start, end = options("time_range_start"), options("time_range_end")

    channel_id, msg_id = tg_channel.id, message.forward_from_message_id

    time_keyboard = select_double_time_keyboard(_PREFIX, start, end, ['set', channel_id, msg_id])

    fmt_text = _("select_time_range", locale=message.from_user.language_code, **{k: fmt_mins(v) for k, v in {"start":
                 start, "end": end, "general_start": start, "general_end": end}.items()})

    await sent_message.edit_text(fmt_text, reply_markup=Keyboard([
        select_double_time_header(),
        *time_keyboard,
        [confirm_btn(_PREFIX, ['confirm', channel_id, msg_id, start, end])]
    ]))


@telegram.on_callback_query(_path("set"))
async def select_forward_time(_, callback_query: CallbackQuery):
    await callback_query.answer()

    channel_id, msg_id, start, end = map(int, callback_query.data.rsplit('_', 4)[1:])

    time_keyboard = select_double_time_keyboard(_PREFIX, start, end, ['set', channel_id, msg_id])

    fmt_text = _("select_time_range", locale=callback_query.from_user.language_code,
                 general_start=options("time_range_start"), general_end=options("time_range_end"),
                 start=fmt_mins(start), end=fmt_mins(end))

    await callback_query.message.edit_text(fmt_text, reply_markup=Keyboard([
        select_double_time_header(),
        *time_keyboard,
        [confirm_btn(_PREFIX, ['confirm', channel_id, msg_id, start, end])]
    ]))


@telegram.on_callback_query(_path("confirm"))
async def confirm_forward_time(_, callback_query: CallbackQuery):
    await callback_query.answer()

    channel_id, msg_id, start, end = map(int, callback_query.data.rsplit('_', 4)[1:])

    if channels.find_one_and_update({"channel_id": channel_id, "scheduling.in_queue": False}, {"$set": {"scheduling": {
            "in_queue": True, "message_id": msg_id, "time_from": start, "time_to": end}}}) is None:
        return await callback_query.message.edit_text(_("already_in_queue",
                                                        locale=callback_query.from_user.language_code))

    await callback_query.message.edit_text(_g("ok"))

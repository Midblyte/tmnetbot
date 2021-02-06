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

from datetime import datetime as dt, timedelta as td, time as t
from typing import Optional, Tuple

import pymongo
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup as Keyboard, InlineKeyboardButton as Button, User, \
    CallbackQuery

from .. import filters as custom_filters
from ..internationalization import translator
from ..mongo import channels, options
from ..telegram import telegram
from ..utils.channels import get_status, ChannelSendingState, ChannelState
from ..utils.general import extract_args, args_joiner
from ..utils.time import fmt_time, fmt_time_duration, is_forwarding_allowed, MINUTES_PER_DAY
from ..utils.users import notify


_PREFIX = "forward",

_, _g = translator(*_PREFIX), translator("general")


@telegram.on_message(filters.private & filters.forwarded)
def forward(__, message: Message):
    locale = getattr(message.from_user, "language_code", None)

    sent_message = message.reply_text(_g("loading", locale=locale))

    if message.forward_from_chat.type != "channel":
        return sent_message.edit_text(_("not_a_channel", locale=locale))

    try:
        status = get_status(message.forward_from_chat.id, message.from_user, tg_channel=message.forward_from_chat)

        _check_forwarding_status(status, locale=locale)
    except ValueError as error:
        error_string, params = error.args

        return sent_message.edit_text(_(error_string, **params, locale=locale))

    _menu(sent_message, message.from_user, message.forward_from_chat.id, message.forward_from_message_id)


@telegram.on_callback_query(custom_filters.arguments(*_PREFIX, "refresh"))
def refresh(__, callback_query: CallbackQuery):
    callback_query.answer()

    forward_from_chat_id, forward_from_message_id = extract_args(callback_query.data, 2, int)

    _menu(callback_query.message, callback_query.from_user, forward_from_chat_id, forward_from_message_id)


@telegram.on_callback_query(custom_filters.arguments(*_PREFIX, "confirm"))
def confirm(__, callback_query: CallbackQuery):
    callback_query.answer()

    locale = getattr(callback_query.from_user, "language_code", None)

    forward_from_chat_id, forward_from_message_id = extract_args(callback_query.data, 2, int)

    try:
        status = get_status(forward_from_chat_id, callback_query.from_user)

        _check_forwarding_status(status, locale=locale)
    except ValueError as error:
        error_string, params = error.args

        return callback_query.message.edit_text(_(error_string, **params, locale=locale))

    dtnow, network_delta, eta = check_forwarding_time(status.queue_length)

    channels.find_one_and_update({"channel_id": forward_from_chat_id}, {"$set": {"scheduling": {
        "in_queue": True,
        "message_id": forward_from_message_id,
        "inserted_on": dtnow,
    }}})

    callback_query.message.edit_text(_("successfully_scheduled", locale=locale))

    start_mins, end_mins = options("time_range_start") or 0, options("time_range_end") or MINUTES_PER_DAY
    start, end = map(lambda minutes: dt.combine(dtnow.date(), t.min) + td(minutes=minutes), (start_mins, end_mins))
    if eta == 0 and is_forwarding_allowed(start, end, dtnow):
        from ..scheduler import periodic_task

        periodic_task.restart()

    reply_markup = lambda user_locale: Keyboard([[
        Button(_("go_to_the_message", locale=user_locale),
               url=f"https://t.me/c/{-forward_from_chat_id + 10**12}/{forward_from_message_id}")]])

    notify("successfully_scheduled", channel_id=forward_from_chat_id, exception=callback_query.from_user.id,
           reply_markup=reply_markup)


def _menu(message: Message, user: User, forward_from_chat_id: int, forward_from_message_id: int):
    locale = user.language_code

    try:
        status = get_status(forward_from_chat_id, user)

        _check_forwarding_status(status, locale=locale)
    except ValueError as error:
        error_string, params = error.args

        return message.edit_text(_(error_string, **params, locale=locale))

    params = lambda action: args_joiner(*_PREFIX, action, forward_from_chat_id, forward_from_message_id)

    keyboard = Keyboard([
        [Button(_g("refresh", locale=locale), params("refresh"))],
        [Button(_g("confirm", locale=locale), params("confirm"))]
    ])

    dtnow, network_delta, eta = check_forwarding_time(status.queue_length)

    wait_string = "no_awaiting_time" if eta == 0 else "awaiting_time"

    fmt_text = '\n'.join([
            _("info", locale=locale),
            _("queue", count=status.queue_length, locale=locale),
            _(wait_string, time=fmt_time_duration(eta, locale), locale=locale),
            _("last_updated_at", time=fmt_time(dt.utcnow(), locale), locale=locale)
        ])

    message.edit_text(fmt_text, reply_markup=keyboard)


def check_forwarding_time(queue_length: int) -> Tuple:
    # todo: let it be recursive to get the real ETA
    network_delta = options("network_delta")
    dtnow = dt.utcnow()
    last_sent_date: dt = (channels.find_one({}, sort=[("last_send", pymongo.DESCENDING)], limit=1,
                                            projection=["last_send"]) or {}).get("last_send", dt.min)

    queue_eta = queue_length * network_delta
    cooldown_eta = max(0, int((last_sent_date + td(seconds=network_delta) - dtnow).total_seconds()))
    eta = queue_eta + cooldown_eta

    return dtnow, network_delta, eta


def _check_forwarding_status(channel_status: ChannelState, locale: Optional[str] = None):
    if channel_status.state == ChannelSendingState.IN_QUEUE:
        raise ValueError("already_in_queue", {})

    if channel_status.state == ChannelSendingState.RESTING:
        raise ValueError("not_allowed_until",
                         {"date": fmt_time(channel_status.last_send + channel_status.delta, locale)})

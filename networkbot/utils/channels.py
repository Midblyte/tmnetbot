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

from collections import namedtuple
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, Union, List

import pymongo
from pyrogram.errors import RPCError
from pyrogram.types import Chat, ChatPreview, User

from .time import fmt_time, fmt_time_duration
from ..internationalization import translator
from ..mongo import channels, options
from ..telegram import telegram


_ = translator("get_channels")


class ChannelSendingState(Enum):
    CAN_SEND = '🔈'
    IN_QUEUE = '⏳'
    RESTING = '🔇'

    def __init__(self, icon):
        self.icon = icon

    def __str__(self):
        return self.icon


ChannelState = namedtuple("ChannelState", ["tg_channel", "channel_doc", "message_id", "name", "default_delta", "delta",
                                           "has_custom_delta", "state", "queue_length", "generation_time", "last_send"])


def get_status(channel_id: int, from_user: Optional[User] = None, *,
               tg_channel: Optional[Union[Chat, ChatPreview]] = None, channel_doc = None) -> ChannelState:
    try:
        if tg_channel is None:
            tg_channel: Union[Chat, ChatPreview] = telegram.get_chat(channel_id)
        if channel_doc is None:
            channel_doc: Optional[Dict] = channels.find_one({"channel_id": channel_id})

        if channel_doc is None:
            raise ValueError("not_part_of_the_network", {"id": channel_id})
    except RPCError:
        raise ValueError("not_a_channel", {"id": channel_id})

    for error_string, member in ("im_not_an_admin", "me"), ("youre_not_an_admin", from_user.id if from_user else None):
        try:
            tg_channel.get_member(member)

            if from_user is None:
                break
        except RPCError:
            raise ValueError(error_string, {})

    channels_queue: List[Dict] = channels.find({"scheduling.in_queue": True}, projection=["delta", "channel_id"],
                                               sort=[("scheduling.inserted_on", pymongo.ASCENDING)])

    now = datetime.utcnow()
    last_send = channel_doc.get("last_send")
    in_queue = channel_doc.get("scheduling").get("in_queue")
    delta = channel_doc.get("delta")
    default_delta = options("channels_delta")

    channels_queue_ids: List[int] = list(map(lambda doc: (doc.get("channel_id"), doc.get("delta")), channels_queue))
    queue_length = channels_queue_ids.index(channel_id) if channel_id in channels_queue_ids else len(channels_queue_ids)

    if in_queue:
        state = ChannelSendingState.IN_QUEUE
    elif last_send is None or last_send + timedelta(seconds=delta or default_delta) < now:
        state = ChannelSendingState.CAN_SEND
    else:
        state = ChannelSendingState.RESTING

    return ChannelState(tg_channel=tg_channel, channel_doc=channel_doc, name=tg_channel.title,
                        default_delta=timedelta(seconds=default_delta), delta=timedelta(seconds=delta or default_delta),
                        has_custom_delta=delta is not None, state=state, queue_length=queue_length,
                        message_id=channel_doc.get("scheduling").get("message_id"),
                        generation_time=channel_doc.get('_id').generation_time,
                        last_send=channel_doc.get('last_send'))


def format_channel_info(channel_id: int, locale=None, detailed=False) -> str:
    status = get_status(channel_id)

    variables = {
        "id": channel_id,
        "name": status.name,
        "icon": status.state.icon,
        "added_on": fmt_time(status.generation_time, locale),
        "last_send": fmt_time(status.last_send, locale),
        "next_send": fmt_time(status.last_send + status.delta, locale),
        "spacing": fmt_time_duration(status.delta.total_seconds(), locale),
    }

    fields = filter(lambda x: bool(x), ("header", "last_send",
                                        "next_send" if status.state != ChannelSendingState.CAN_SEND else None,
                                        "added_on" if detailed else None, "spacing" if detailed else None))

    return '\n'.join(map(lambda key: _(f"channel_{key}", **variables, locale=locale), fields))
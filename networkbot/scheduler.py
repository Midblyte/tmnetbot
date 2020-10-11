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

import asyncio
from datetime import datetime as dt, time as t, timedelta
from threading import Timer, Lock, Thread
from typing import Dict, Union, List

import pymongo
from pyrogram.types import Message, InlineKeyboardMarkup as Keyboard, InlineKeyboardButton as Button

from .internationalization import translator
from .mongo import options, channels
from .network import network
from .telegram import telegram
from .utils.time import MINUTES_PER_DAY, is_forwarding_allowed
from .utils.users import notify


_, _n = translator("schedule"), translator("settings", "notifications")


class PeriodicTask:
    def __init__(self, run, interval):
        self._lock = Lock()
        self._timer = None
        self._interval = interval
        self._run = run
        self._running = False

    def _run_fn(self):
        if asyncio.iscoroutinefunction(self._run):
            asyncio.run(self._run())
        else:
            self._run()

    def start(self, force=False):
        self._lock.acquire()

        Thread(target=self._run_fn).start()

        if not self._running or force:
            self._running = True
            self._timer = Timer(self._interval, lambda: self.start(True))
            self._timer.start()

            self._lock.release()

    def stop(self):
        self._lock.acquire()
        self._running = False
        self._timer.cancel()
        self._lock.release()

    def restart(self):
        self.stop()
        self.start()


def get_channels_in_queue(limit: int = 1) -> List[Dict]:
    return list(channels.aggregate([
        {"$match": {"scheduling.in_queue": True}},
        {"$sort": {"scheduling.inserted_on": pymongo.ASCENDING}},
        {"$limit": limit},
        {"$lookup": {
            "from": "users",
            "localField": "administrators",
            "foreignField": "user_id",
            "as": "administrators"
        }},
        {"$match": {"administrators.notifications.sending": True}},
        {"$project": {
            "users_ids": "$administrators.user_id",
            "channel_id": True,
            "message_id": "$scheduling.message_id"
        }}
    ]))


def check_and_send():
    queue: List[Dict] = get_channels_in_queue(1)

    start_mins, end_mins = options("time_range_start") or 0, options("time_range_end") or MINUTES_PER_DAY

    datetime_now = dt.utcnow()
    today = datetime_now.date()
    start, end = map(lambda minutes: dt.combine(today, t.min) + timedelta(minutes=minutes), (start_mins, end_mins))

    if len(queue) == 0 or not is_forwarding_allowed(start, end, datetime_now):
        return

    for channel in queue:
        channel_id, message_id = channel.get("channel_id"), channel.get("message_id")

        sent_message: Union[Message, List[Message]] = telegram.forward_messages(network, channel_id, message_id)

        channels.update_one({"_id": channel.get("_id")},
                            {"$set": {"last_send": datetime_now, "scheduling": {"in_queue": False}}})

        sent_msg_id = (sent_message[0] if isinstance(sent_message, list) else sent_message).message_id

        reply_markup = lambda locale: Keyboard([[Button(_("go_to_the_message", locale=locale),
                                                        url=f"https://t.me/c/{-channel_id + 10**12}/{sent_msg_id}")]])

        notify("successfully_forwarded", users_ids=channel.get("users_ids"), reply_markup=reply_markup)

    # todo notify: cooldown_ended


periodic_task = PeriodicTask(check_and_send, options("network_delta"))

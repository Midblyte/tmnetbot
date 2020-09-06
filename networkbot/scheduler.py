from datetime import datetime as dt, time as t, timedelta
from threading import Timer, Lock
from typing import Optional, Dict, Union, List

import pymongo
from pyrogram.errors import RPCError
from pyrogram.types import Message, InlineKeyboardMarkup as Keyboard, InlineKeyboardButton as Button

from .helpers import minutes_in_a_day
from .mongo import options, channels
from .network import network
from .telegram import telegram


successfully_forwarded = "\
Messaggio inoltrato"

go_to_the_message = "\
Vai al messaggio"


class PeriodicMongoTask:
    def __init__(self):
        self._lock = Lock()
        self._timer = None
        self._running = False

    @staticmethod
    def _check():
        collection_filter = {"scheduling.in_queue": True}
        collection_sort = [
            ("_id", pymongo.ASCENDING),
            ("scheduling.time_to", pymongo.ASCENDING)
        ]
        to_be_sent: Optional[Dict] = channels.find_one(collection_filter, sort=collection_sort)
        documents_number = channels.count_documents(collection_filter)

        if documents_number == 0:
            return

        start_min, end_min = options("time_range_start") or 0, options("time_range_end") or minutes_in_a_day

        datetime_now = dt.utcnow()
        today = datetime_now.date()
        start = dt.combine(today, t.min) + timedelta(minutes=start_min)
        end = dt.combine(today, t.min) + timedelta(minutes=end_min)
        inclusive = True

        if start > end:
            start, end = end, start
            inclusive = False

        if start < datetime_now < end and not inclusive:
            return

        channel_id, message_id = to_be_sent.get("channel_id"), to_be_sent.get("scheduling").get("message_id")

        sent_message: Union[Message, List[Message]] = telegram.forward_messages(network, channel_id, message_id)

        channels.update_one(to_be_sent, {"$set": {"last_send": datetime_now, "scheduling": {"in_queue": False}}})

        channel_username, msg_id = sent_message.chat.username, sent_message.message_id
        reply_markup = None
        if channel_username:
            reply_markup = Keyboard([[Button(go_to_the_message, url=f"https://t.me/{channel_username}/{msg_id}")]])

        for administrator_id in to_be_sent.get("administrators"):
            try:
                telegram.send_message(administrator_id, successfully_forwarded, reply_markup=reply_markup)
            except RPCError:
                pass

    def start(self, force=False):
        self._lock.acquire()

        if not self._running or force:
            self._running = True
            self._check()
            self._timer = Timer(options("network_delta"), lambda: self.start(True))
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


periodic_task = PeriodicMongoTask()

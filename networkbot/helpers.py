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

from itertools import islice
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Callable, Dict, Any, Iterable

import pytz
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


minutes_in_a_day = 24 * 60


def chunk(iterable: Iterable[Any], size: int):
    iter_copy = iter(iterable)
    return iter(lambda: tuple(islice(iter_copy, size)), ())


def fmt_time(dt, fmt="%d/%m/%Y %H:%M:%S", timezone="Europe/Rome", never="mai") -> str:
    if dt == datetime.min:
        return never
    return (pytz.utc.localize(dt) if dt.tzinfo is None else dt).astimezone(pytz.timezone(timezone)).strftime(fmt)


def get_documents_range(collection: Collection, offset=0, maximum_per_page=10, filters=None,
                        nav: Callable[[Collection, int], str] = None) -> Tuple[Cursor, Optional[InlineKeyboardMarkup]]:
    if filters is None:
        filters = {}

    if nav is None:
        nav = lambda c, o: f"{c}_nav_{o}"

    documents: Cursor = collection.find(filters).skip(offset*maximum_per_page).limit(maximum_per_page)
    documents_number = collection.count_documents(filters)

    if documents_number <= maximum_per_page and offset == 0:
        return documents, None

    nav_buttons: List[InlineKeyboardButton] = []

    if offset > 0:
        nav_buttons.append(InlineKeyboardButton("«", callback_data=nav(collection.name, offset-1)))

    if documents_number > maximum_per_page * (offset + 1):
        nav_buttons.append(InlineKeyboardButton("»", callback_data=nav(collection.name, offset+1)))

    return documents, InlineKeyboardMarkup([nav_buttons])


def format_documents_list(cursor: Cursor, fmt_function: Callable[[Dict], str], separator='\n\n') -> str:
    return separator.join([fmt_function(c) for c in cursor])


def dummy_btn(text: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text, "dummy")


def localize_minutes(minutes: int, timezone=pytz.timezone("Europe/Rome")):
    value = minutes + datetime.utcnow().astimezone(timezone).tzinfo.utcoffset(datetime.utcnow()).seconds // 60

    if 0 < value < minutes_in_a_day:
        return value
    else:
        return (minutes_in_a_day + value) % minutes_in_a_day


def can_send_icon(last_send_time: datetime, delta_time: int, in_queue: bool, default_delta: int):
    now: datetime = datetime.utcnow()
    last_send = last_send_time or datetime.min
    delta = timedelta(seconds=delta_time or default_delta)

    if in_queue:
        return "⏳"
    elif last_send + delta > now:
        return "🔇"
    else:
        return "🔈"

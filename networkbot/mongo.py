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

from typing import Any, Callable

import pymongo
from pymongo import MongoClient, IndexModel
from pymongo.collection import Collection
from pymongo.database import Database

from .config import config
from .utils.time import MINUTES_PER_DAY


mongo = MongoClient(config.MONGO_URL)
networkdb: Database = mongo[config.NETWORK_SHORT_NAME]
users: Collection = networkdb.users
channels: Collection = networkdb.channels
options_collection: Collection = networkdb.options
options: Callable[[str], Any] = lambda field: options_collection.find_one({}, projection=[field]).get(field)


def init():
    from . import __version__

    defaults = {
        "channels_delta": 3 * MINUTES_PER_DAY * 60,  # Each channel admin can send a message every 3 days, in seconds
        "network_delta": 30 * 60,  # Messages are sent within a delay of 30 minutes, in seconds
        "time_range_start": 8 * 60,  # Posting is enabled since 08:00 a.m. UTC, in minutes
        "time_range_end": 16 * 60,  # Posting is enabled until 08:00 p.m UTC, in minutes
        "__version__": __version__
    }

    options_collection.update_one({}, {"$setOnInsert": defaults}, upsert=True)

    _create_indexes()



def _create_indexes():
    channels_indexes: List[IndexModel] = [
        IndexModel([("channel_id", pymongo.ASCENDING)], unique=True),
        IndexModel([("administrators", pymongo.ASCENDING)]),
        IndexModel([("last_send", pymongo.DESCENDING)]),
        IndexModel([("scheduling.in_queue", pymongo.ASCENDING)])
    ]
    users_indexes: List[IndexModel] = [
        IndexModel([("user_id", pymongo.ASCENDING)], unique=True),
        IndexModel([("admin", pymongo.ASCENDING)])
    ]

    channels.create_indexes(channels_indexes)
    users.create_indexes(users_indexes)

import os
from typing import Any, Callable, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from .config import config
from .helpers import minutes_in_a_day

mongo = MongoClient(config.get("MONGO_URL"))
networkdb: Database = mongo[os.getenv("NETWORK_SHORT_NAME", "tmnetbot")]
admins: Collection = networkdb.admins
channels: Collection = networkdb.channels
_options_collection: Collection = networkdb.options
options: Callable[[str], Any] = lambda field: _options_collection.find_one({}, projection=[field]).get(field)


def init():
    defaults = {
        "channels_delta": 3 * minutes_in_a_day * 60,  # Each channel admin can send a message every 3 days, in seconds
        "network_delta": 30 * 60,  # Messages are sent within a delay of 30 minutes, in seconds
        "time_range_start": 8 * 60,  # Posting is enabled since 08:00 a.m. UTC, in minutes
        "time_range_end": 16 * 60,  # Posting is enabled until 08:00 p.m UTC, in minutes
    }

    _options_collection.update_one({}, {"$setOnInsert": defaults}, upsert=True)

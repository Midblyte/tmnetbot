import sys

from pyrogram.scaffold import Scaffold
import dotenv


dotenv.load(Scaffold.PARENT_DIR / '..' / ".env")

config = {}

_entries = {
    "telegram": {
        "api_id": True,
        "api_hash": True,
        "bot_token": True,
        "channel": True
    },
    "mongo": {
        "url": True
    },
    "network": {
        "short_name": False
    }
}

for section, options in _entries.items():
    for option, is_required in options:
        key = '_'.join([section, option]).upper()
        value = dotenv.get(key, default=None)
        if is_required and value is None:
            sys.exit(f"Environment variable not found: '{key}'")
        config[key] = value

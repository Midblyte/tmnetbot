import sys

from pyrogram.scaffold import Scaffold
import dotenv


dotenv.load(Scaffold.PARENT_DIR / '..' / ".env")

config = {}

_entries = {
    "telegram": {"api_id", "api_hash", "bot_token", "channel"},
    "mongo": {"url"},
    "network": {"short_name"}
}

for section, options in _entries.items():
    for option in options:
        key = '_'.join([section, option]).upper()
        value = dotenv.get(key, default=None)
        if value is None:
            sys.exit(f"Environment variable not found: '{key}'")
        config[key] = value

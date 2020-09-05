from pyrogram import idle

from . import handlers
from .scheduler import periodic_task
from .config import config
from .core import main


__version__ = "0.1.0"
__license__ = "MIT License"
__copyright__ = "Copyright (C) 2020 Midblyte <https://github.com/Midblyte>"


def start():
    core.main()

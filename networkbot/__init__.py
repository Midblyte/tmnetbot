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

from .scheduler import periodic_task
from .config import config
from .core import main
from . import handlers


__version__ = "0.1.0"
__license__ = "GNU General Public License v3 or later (GPLv3+)"
__copyright__ = "Copyright (C) 2020 Midblyte <https://github.com/Midblyte>"


def start():
    from . import upgrader

    core.main()

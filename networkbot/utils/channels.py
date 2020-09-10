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

from datetime import datetime, timedelta


def can_send_icon(last_send_time: datetime, delta_time: int, in_queue: bool):
    now: datetime = datetime.utcnow()
    last_send: datetime = last_send_time or datetime.min
    delta = timedelta(seconds=delta_time)

    if in_queue:
        return '⏳'
    elif last_send + delta > now:
        return '🔇'
    else:
        return '🔈'

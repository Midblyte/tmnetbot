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

from datetime import datetime

import pytz

MINUTES_PER_DAY = 24 * 60


def fmt_time(dt, fmt="%d/%m/%Y %H:%M:%S", timezone="Europe/Rome", never="mai") -> str:
    if dt is None:
        return never
    return (pytz.utc.localize(dt) if dt.tzinfo is None else dt).astimezone(pytz.timezone(timezone)).strftime(fmt)


def localize_minutes(minutes: int, timezone=pytz.timezone("Europe/Rome")) -> int:
    value = minutes + datetime.utcnow().astimezone(timezone).tzinfo.utcoffset(datetime.utcnow()).seconds // 60

    return fix_minutes(value)


def fmt_mins(minutes: int, transform_function=localize_minutes) -> str:
    if transform_function is not None:
        minutes = transform_function(minutes)

    return '{:02}:{:02}'.format(minutes // 60, minutes % 60)


def fix_minutes(minutes: int) -> int:
    if 0 < minutes < MINUTES_PER_DAY:
        return minutes
    else:
        return (MINUTES_PER_DAY + minutes) % MINUTES_PER_DAY

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
from typing import Optional

import pytz

from ..internationalization import translator


_ = translator("time")

MINUTES_PER_DAY = 24 * 60


def fmt_time(dt, locale: Optional[str] = None) -> str:
    if dt is None:
        return _("never")

    return (pytz.utc.localize(dt) if dt.tzinfo is None else dt) \
        .astimezone(pytz.timezone(_("timezone", locale=locale))) \
        .strftime(_("date_full_format", locale=locale))


def fmt_time_duration(seconds: int, locale=None):
    fmt = _("interval_full_format", locale=locale)

    entries = (('d', int(seconds / 60 / 60 / 24)),
               ('total_H', int(seconds / 60 / 60)),
               ('H', int(seconds / 60 / 60 % 24)),
               ('total_M', int(seconds / 60)),
               ('M', int(seconds / 60 % 60)),
               ('total_S', seconds),
               ('S', seconds % 60))

    for k, v in entries:
        fmt = fmt.replace(f"%{k}", str(v))

    return fmt


def localize_minutes(minutes: int, timezone=pytz.timezone("Europe/Rome")) -> int:
    value = minutes + datetime.utcnow().astimezone(timezone).tzinfo.utcoffset(datetime.utcnow()).seconds // 60

    return fix_minutes(value)


def fmt_mins(minutes: int, transform_function=localize_minutes) -> str:
    if transform_function is not None:
        minutes = transform_function(minutes)

    return '{:02}:{:02}'.format(minutes // 60, minutes % 60)


def ranged_value(value: int, _max: int, _min: int = 0, starting_from: int = 0) -> int:
    return max(_min, (value - _min) % (_max - _min) + _min + starting_from)


def fix_minutes(num: int):
    return ranged_value(num, MINUTES_PER_DAY)

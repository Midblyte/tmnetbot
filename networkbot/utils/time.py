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

from ..internationalization import translator


_ = translator("time")

MINUTES_PER_DAY = 24 * 60


def fmt_time(dt) -> str:
    # TODO: "locale" param is missing
    if dt is None:
        return _("never")

    return (pytz.utc.localize(dt) if dt.tzinfo is None else dt) \
        .astimezone(pytz.timezone(_("timezone"))) \
        .strftime(_("full_format"))


def fmt_time_duration(seconds: int):
    # TODO: "locale" param is missing
    fmt = _("interval_full_format")

    for k, v in (
             # Days
             ('d', int(seconds / 60 / 60 / 24)),

             # Hours
             ('total_H', int(seconds / 60 / 60)),
             ('H', int(seconds / 60 / 60 % 24)),

             # Minutes
             ('total_M', int(seconds / 60)),
             ('M', int(seconds / 60 % 60)),

             ('total_S', seconds),
             ('S', seconds % 60)):
        fmt = fmt.replace(f"%{k}", v)

    return fmt


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

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

from typing import Callable, Iterable


def evaluate(var_or_func, *args, **kwargs):
    return var_or_func(*args, **kwargs) if isinstance(var_or_func, Callable) else var_or_func


def args_joiner(*args, separator='_'):
    return separator.join(map(str, args))


def extract_args(data: str, args_number, fn = str) -> Iterable:
    return map(fn, data.rsplit('_', args_number)[-args_number:])

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

from typing import Iterable, Any, List

from pyrogram.types import InlineKeyboardButton as Button

from .time import fix_minutes


_BUTTONS = ('1m', 1), ('15m', 15), ('1h', 60), ('4h', 240)

from_text = "Da"

to_text = "A"

confirm_text = "Conferma"


def select_time_keyboard(prefix: str, time: int, args: Iterable[Any] = None):
    if args is None:
        args = []

    time_keyboard = []
    for label, value in _BUTTONS:
        time_keyboard.append(select_time_row(label, value, prefix, fix_minutes(time), args))

    return time_keyboard


def select_time_row(label: str, value: int, prefix: str, time: int, args: Iterable[Any] = None) \
                                                                                                        -> List[Button]:
    buttons_row: List[Button] = []

    if args is None:
        args = []

    for i in range(2):
        sign = i % 2

        change = +value if sign == 0 else -value

        buttons_row.append(custom_btn(f"{'+-'[sign]}{label}", prefix, [*args, fix_minutes(change + value)]))

    return buttons_row


def select_double_time_keyboard(prefix: str, start: int, end: int, args: Iterable[Any] = None) -> List[List[Button]]:
    if args is None:
        args = []

    start, end = map(fix_minutes, (start, end))

    time_keyboard = []
    for label, value in _BUTTONS:
        time_keyboard.append(select_double_time_row(label, value, prefix, start, end, args))

    return time_keyboard


def select_double_time_header() -> List[Button]:
    return [dummy_btn(from_text), dummy_btn(to_text)]


def select_double_time_row(label: str, value: int, prefix: str, start: int, end: int, args: Iterable[Any] = None) \
                                                                                                        -> List[Button]:
    buttons_row: List[Button] = []

    if args is None:
        args = []

    for i in range(4):
        start_time, end_time = start, end
        sign, side = i % 2, i // 2

        change = +value if sign == 0 else -value

        if side == 0:
            start_time = fix_minutes(start + change)
        else:
            end_time = fix_minutes(end + change)

        buttons_row.append(custom_btn(f"{'+-'[sign]}{label}", prefix, [*args, start_time, end_time]))

    return buttons_row


def custom_btn(label: str, prefix: str, args: Iterable[Any]) -> Button:
    return Button(label, f"{'_'.join(map(str, [prefix, *args]))}")


def dummy_btn(label: str) -> Button:
    return Button(label, "dummy")


def confirm_btn(prefix: str, args: Iterable[Any]) -> Button:
    return custom_btn(confirm_text, prefix, args)

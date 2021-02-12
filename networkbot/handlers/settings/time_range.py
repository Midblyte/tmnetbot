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

from typing import List, Tuple

from pyrogram.types import InlineKeyboardButton as Button, User, Message

from ...internationalization import translator
from ...mongo import options, options_collection
from ...utils.general import args_joiner
from ...utils.keyboards import handle_double_keyboard, dummy_btn
from ...utils.time import fmt_mins, fix_minutes


_PREFIX = "settings", "time_range"

_BACK = "settings", "initial"

_BUTTONS = ('1m', 1), ('15m', 15), ('1h', 60), ('4h', 240)

_, _g, _t = translator(*_PREFIX), translator("general"), translator("time")


def get_defaults() -> Tuple[int, int]:
    return options("time_range_start"), options("time_range_end"),


def text(user: User, *values: int) -> str:
    start, end = values

    return _("info", locale=user.language_code, start=fmt_mins(start), end=fmt_mins(end))


def buttons_before(user: User, *__) -> List[List[Button]]:
    return [[dummy_btn(_t(label, locale=user.language_code)) for label in ("from", "to")]]


def buttons_after(user: User, *__) -> List[List[Button]]:
    return [[Button(_g("back", locale=user.language_code), args_joiner(*_BACK))]]


async def on_confirm(message: Message, user: User, *values: int) -> None:
    start, end = values

    await message.edit_text(_("info", locale=user.language_code, start=fmt_mins(start), end=fmt_mins(end)))

    options_collection.find_one_and_update({}, {"$set": {"time_range_start": start, "time_range_end": end}})


handle_double_keyboard(*_PREFIX, map_fn=fix_minutes, defaults=get_defaults, columns_number=2, buttons=_BUTTONS,
                       buttons_before=buttons_before, buttons_after=buttons_after, text=text, on_confirm=on_confirm)

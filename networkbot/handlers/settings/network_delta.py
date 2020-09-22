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
from ...utils.keyboards import handle_double_keyboard
from ...utils.time import fmt_time_duration, ranged_value


_PREFIX = "settings", "network_delta"

_BACK = "settings", "initial"

_BUTTONS = ('1s', 1), ('30s', 30), ('15m', 900), ('2h', 7200)

_, _g = translator(*_PREFIX), translator("general")


def get_defaults() -> Tuple[int]:
    return options("network_delta"),


def text(user: User, *values: int) -> str:
    locale = user.language_code

    return _("info", locale=locale, interval=fmt_time_duration(values[0], locale))


def buttons_after(user: User, *__) -> List[List[Button]]:
    return [[Button(_g("back", locale=user.language_code), args_joiner(*_BACK))]]


async def on_confirm(message: Message, user: User, *values: int) -> None:
    locale = user.language_code

    await message.edit_text(_("info", locale=locale, interval=fmt_time_duration(values[0], locale)))

    options_collection.find_one_and_update({}, {"$set": {"network_delta": values[0]}})


handle_double_keyboard(*_PREFIX, map_fn=lambda n: ranged_value(n, 30 * 24 * 60 * 60, 0), defaults=get_defaults,
                       buttons=_BUTTONS, buttons_after=buttons_after, text=text, on_confirm=on_confirm)

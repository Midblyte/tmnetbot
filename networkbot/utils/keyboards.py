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

from typing import Iterable, List, Tuple, Callable, Optional

from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup as Keyboard, InlineKeyboardButton as Button, \
    User

from .general import evaluate, args_joiner, extract_args
from .. import filters as custom_filters
from ..internationalization import translator
from ..telegram import telegram


_ = translator("general")


def dummy_btn(label: str) -> Button:
    return Button(label, "dummy")


def generate_pattern_buttons(*prefix, pattern: Iterable[Tuple[str, int]],
                             btn_text: Callable[[str, str, User], str] = lambda sign, label, user: f"{sign}{label}") \
        -> Callable[..., List[List[Button]]]:
    def func(user: User, *args):
        buttons_rows = []

        for label, change in pattern:
            row = []

            for i, value in enumerate(args):
                plus, minus = list(args), list(args)

                plus[i] += change
                minus[i] -= change

                for sign, parameters in ('+', plus), ('-', minus):
                    row.append(Button(btn_text(sign, label, user), args_joiner(*prefix, 'set', *parameters)))

            buttons_rows.append(row)

        return buttons_rows

    return func


def handle_double_keyboard(*prefix, defaults, text, columns_number: int = 1, map_fn: Callable[[int], int] = lambda n: n,
                           buttons, buttons_before=None, buttons_after=None, on_confirm: Optional[Callable]) -> None:
    _, _g = translator("settings"), translator("general")

    buttons_pattern = generate_pattern_buttons(*prefix, pattern=buttons)

    async def edit_message(message: Message, user: User, *args: int):
        msg_text = evaluate(text, user, *args)

        kb = Keyboard([
            *(evaluate(buttons_before, user, *args) or []),
            *(evaluate(buttons_pattern, user, *args) or []),
            [Button(_g("confirm", locale=user.language_code), args_joiner(*prefix, "confirm", *args))],
            *(evaluate(buttons_after, user, *args) or [])
        ])

        await message.edit_text(msg_text, reply_markup=kb)

    @telegram.on_callback_query(custom_filters.arguments(*prefix, "initial"))
    async def initial(__, callback_query: CallbackQuery):
        await callback_query.answer()

        await edit_message(callback_query.message, callback_query.from_user, *evaluate(defaults))

    @telegram.on_callback_query(custom_filters.arguments(*prefix, "set"))
    async def _set(__, callback_query: CallbackQuery):
        await callback_query.answer()

        args = map(map_fn, extract_args(callback_query.data, columns_number, int))

        await edit_message(callback_query.message, callback_query.from_user, *args)

    @telegram.on_callback_query(custom_filters.arguments(*prefix, "confirm"))
    async def confirm(__, callback_query: CallbackQuery):
        await callback_query.answer()

        args = map(map_fn, extract_args(callback_query.data, columns_number, int))

        if on_confirm is not None:
            await on_confirm(callback_query.message, callback_query.from_user, *args)

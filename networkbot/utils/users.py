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

from typing import List, Literal, Iterable, Optional, Callable

from pyrogram.errors import PeerIdInvalid, RPCError
from pyrogram.types import User, InlineKeyboardMarkup

from ..internationalization import translator
from ..mongo import channels
from ..telegram import telegram


_n = translator("settings", "notifications")


def safe_map_ids_to_users(ids: Iterable[int]) -> List[User]:
    tg_users = []

    try:
        tg_users.extend(telegram.get_users(ids))  # try a faster method
    except PeerIdInvalid:  # fallback, just in case the previous call fails
        for uid in ids:
            try:
                tg_users.append(telegram.get_users(uid))
            except RPCError:
                pass

    return tg_users


def notify(event: Literal["successfully_scheduled", "scheduling_cancelled", "successfully_forwarded", "cooldown_ended"],
           *,
           channel_id: Optional[int] = None,
           users_ids: Optional[Iterable[int]] = None,
           exception: Optional[int] = None,
           reply_markup: Optional[Callable[[str], InlineKeyboardMarkup]] = None):

    if channel_id is None and users_ids is None:
        raise ValueError('Neither "channel_id" nor "users_ids" was passed', {})

    if channel_id is not None:
        key = {
            "successfully_scheduled": "scheduling",
            "scheduling_cancelled": "scheduling",
            "successfully_forwarded": "sending",
            "cooldown_ended": "cooldown"
        }[event]

        users_ids = list(channels.aggregate([
            {"$match": {"channel_id": channel_id}},
            {"$lookup": {
                "from": "users",
                "localField": "administrators",
                "foreignField": "user_id",
                "as": "administrators"
            }},
            {"$match": {f"administrators.notifications.{key}": True}},
            {"$project": {"users_ids": "$administrators.user_id"}}
        ]))[0].get("users_ids", [])

    tg_users: List[User] = safe_map_ids_to_users(users_ids)

    for tg_user in tg_users:
        if tg_user.id == exception:
            continue

        admin_locale = tg_user.language_code

        try:
            telegram.send_message(tg_user.id, _n(event, locale=admin_locale, mention=tg_user.mention, id=tg_user.id,
                                                 first_name=tg_user.first_name, last_name=tg_user.first_name),
                                  reply_markup=reply_markup(admin_locale) if reply_markup else None)
        except RPCError:
            pass

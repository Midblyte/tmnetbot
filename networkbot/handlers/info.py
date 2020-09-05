from typing import Dict

from pymongo.cursor import Cursor
from pyrogram import filters
from pyrogram.types import Message

from ..helpers import format_documents_list, can_send_icon
from ..mongo import channels, options
from ..telegram import telegram


not_an_admin = "\
Non sei admin di alcun canale"

admin_of_these_channels = "\
Canali di cui sei admin:\n\n{channels}"


@telegram.on_message(filters.private & filters.command(["info"]))
async def info(_, message: Message):
    collection_filter = {"administrators": {"$in": [message.from_user.id]}}
    admin_of_channels: Cursor = channels.find(collection_filter)
    count = channels.count_documents(collection_filter)

    if count == 0:
        return await message.reply_text(not_an_admin)

    fmt_channels = format_documents_list(admin_of_channels, _get_info)

    await message.reply_text(admin_of_these_channels.format(channels=fmt_channels))


def _get_info(channel: Dict) -> str:
    return f"""\
{can_send_icon(channel.get('last_send_time'), channel.get('delta'), channel.get("scheduling.in_queue"), options('channels_delta'))}
Canale: <b>{channel.get('name')}</b>"""

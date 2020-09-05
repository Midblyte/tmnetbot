from pyrogram import filters
from pyrogram.types import Message

from ..mongo import channels
from ..telegram import telegram


@telegram.on_message(filters.new_chat_title & filters.channel)
async def on_channel_name_change(_, message: Message):
    channels.find_one_and_update({"channel_id": message.chat.id}, {"$set": {"name": message.chat.title}})

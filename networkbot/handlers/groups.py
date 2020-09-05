from pyrogram import filters
from pyrogram.types import Message

from ..telegram import telegram


channels_only = "\
Posso essere aggiunto solo nei canali"


@telegram.on_message((filters.group_chat_created | filters.new_chat_members) & filters.group)
async def added_in_a_group(_, message: Message):
    await message.reply_text(channels_only)
    await message.chat.leave()

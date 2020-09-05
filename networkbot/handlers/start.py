from pyrogram import filters
from pyrogram.types import Message

from ..telegram import telegram


start_info = """\
Ciao {},

Digita /aiuto per maggiori informazioni sul funzionamento del bot"""


@telegram.on_message(filters.private & filters.command("start"))
async def start(_, message: Message):
    await message.reply_text(start_info.format(message.from_user.mention))
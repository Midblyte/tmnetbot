from pyrogram import filters
from pyrogram.types import Message

from .. import filters as custom_filters
from ..mongo import admins
from ..telegram import telegram


makemeadmin_info = """\
Ora sei admin.

Nota: a partire da questo momento il comando non funzionerà più."""


@telegram.on_message(filters.private & filters.command("makemeadmin") & custom_filters.no_admins)
async def make_me_admin(_, message: Message):
    admins.insert_one({"user_id": message.from_user.id, "name": message.from_user.first_name})

    await message.reply_text(makemeadmin_info)

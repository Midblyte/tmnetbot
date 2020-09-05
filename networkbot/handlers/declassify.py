from pyrogram import filters, Client
from pyrogram.errors import RPCError
from pyrogram.types import Message

from .promote import not_an_user
from .. import filters as custom_filters
from ..mongo import admins
from ..telegram import telegram


usage = "\
Uso: /declassa @Username\n\nAlias: /declassify"

unlisted_admin = "\
L'admin non è nella lista."

successfully_removed = "\
Rimosso {} ({}) da admin."


@telegram.on_message(filters.private & filters.command(["declassa", "declassify"]) & custom_filters.is_admin)
async def declassify(client: Client, message: Message):
    if ' ' not in message.text:
        return await message.reply_text(usage)

    user_as_text = message.text.split(' ')[1]

    try:
        admin = await client.get_users(user_as_text)
    except RPCError:
        return await message.reply_text(not_an_user)

    if admins.find_one_and_delete({"user_id": admin.id}) is None:
        await message.reply_text(unlisted_admin)
    else:
        await message.reply_text(successfully_removed.format(admin.first_name, admin.id))

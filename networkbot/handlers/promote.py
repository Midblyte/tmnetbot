from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.errors import RPCError

from .. import filters as custom_filters
from ..mongo import admins
from ..telegram import telegram


usage = "\
Uso: /promuovi @Username\n\nAlias: /promote"

already_listed_admin = "\
L'admin è già in lista."

not_an_user = "\
Non è un utente"

promote_successful = "\
Aggiunto {} ({}) come amministratore."


@telegram.on_message(filters.private & filters.command(["promuovi", "promote"]) & custom_filters.is_admin)
async def promote(client: Client, message: Message):
    if ' ' not in message.text:
        return await message.reply_text(usage)

    user_as_text = message.text.split(' ')[1]

    try:
        admin = await client.get_users(user_as_text)
    except RPCError:
        return await message.reply_text(not_an_user)

    if admins.find_one({"user_id": admin.id}):
        return await message.reply_text(already_listed_admin)

    admins.insert_one({"user_id": admin.id, "name": admin.first_name})
    await message.reply_text(promote_successful.format(admin.first_name, admin.id))

from pyrogram import filters
from pyrogram.types import Message

from ..mongo import admins
from ..telegram import telegram


help_for_users = """\
<b>Messaggio di aiuto</b>:

<b>Comando /start</b>
» Avvia il bot

<b>Comando /aiuto</b>
» Visualizza questo messaggio
Alias: /help

<b>Comando /info</b>
» Per conoscere quando ti sarà possibile inviare nuovamente un messaggio nel tuo canale, digita /info

<b>Inoltro di messaggio</b>
» Se mi inoltri un messaggio da un tuo canale, provvederò ad inviarlo nel canale del network."""

help_for_admins = """\n\n\n\n\
<b>Per gli amministratori</b>:

<b>Comando /canali</b>
» Elenco dei canali che sono parte del network
Alias: /channels

<b>Comando /amministratori</b>
» Elenco degli admin di questo bot e del network (non dei singoli canali)
Alias: /admins, admin

<b>Comando /aggiungi @username</b>
» Inserisci un nuovo canale
Alias: /add, /inserisci

<b>Comando /rimuovi @username</b>
» Rimuovi un canale
Alias: /remove, /rm

<b>Comando /promuovi @username</b>
» Aggiungi un admin
Alias: /promote

<b>Comando /declassa @username</b>
» Rimuovi un admin
Alias: /declassify


Nota: invece degli username, puoi specificare anche gli ID numerici"""


@telegram.on_message(filters.private & filters.command(["help", "aiuto"]))
async def help_command(_, message: Message):
    is_admin = admins.find_one({"user_id": message.from_user.id})

    help_msg = help_for_users

    if is_admin:
        help_msg += help_for_admins

    await message.reply_text(help_msg)

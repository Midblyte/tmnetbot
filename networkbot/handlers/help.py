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
» Per conoscere quando ti sarà possibile inviare nuovamente un messaggio nel tuo canale

<b>Inoltro di messaggio</b>
» Se mi inoltri un messaggio da un tuo canale, provvederò ad inviarlo nel canale del network."""

help_for_admins = """\n\n\n\n\
<b>Per gli amministratori</b>:

<b>Comando /canali</b>
» Elenco dei canali che sono parte del network
Alias: /channels

<b>Comando /amministratori</b>
» Elenco degli admin di questo bot e del network (non dei singoli canali)
Alias: /admins, /admin

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

<b>Comando /impostazioni</b>
» Imposta la fascia oraria consentita per l'invio degli inoltri, più il loro distanziamento
Alias: /settings

Nota: invece degli username, puoi specificare anche gli ID numerici"""


@telegram.on_message(filters.private & filters.command(["help", "aiuto"]))
async def help_command(_, message: Message):
    is_admin = admins.find_one({"user_id": message.from_user.id})

    help_msg = help_for_users

    if is_admin:
        help_msg += help_for_admins

    await message.reply_text(help_msg)

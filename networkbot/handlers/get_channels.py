from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from .. import filters as custom_filters
from ..helpers import get_documents_range, format_documents_list, fmt_time, chunk, can_send_icon
from ..mongo import channels, options
from ..telegram import telegram


loading_channels = "\
Caricamento lista canali..."

channels_zero = """\
Non ci sono canali in lista.
Aggiungili con /aggiungi @username"""

channels_list = "\
<b>Elenco dei canali</b>:\n\n{channels}"

go_back = "\
« Indietro"


@telegram.on_message(filters.private & filters.command(["channels", "canali"]) & custom_filters.is_admin)
async def get_channels(_, message: Message):
    if channels.count_documents({}) == 0:
        return await message.reply_text(channels_zero)

    await _navigate(await message.reply_text(loading_channels))


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith(f"{channels.name}_nav_")))
async def get_channels_page(_, callback_query: CallbackQuery):
    offset = int(callback_query.data.rsplit('_', 1)[1])

    await callback_query.answer()

    await _navigate(callback_query.message, offset)


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data.startswith(f"{channels.name}_info_")))
async def get_channel_info(_, callback_query: CallbackQuery):
    channel_id, back_offset = map(int, callback_query.data.rsplit('_', 2)[1:])

    channel = channels.find_one({"channel_id": channel_id})

    await callback_query.answer()

    await callback_query.message.edit_text(channel.get("name"), reply_markup=InlineKeyboardMarkup([[
        InlineKeyboardButton(go_back, f"{channels.name}_nav_{back_offset}")
    ]]))


async def _navigate(message: Message, offset=0):
    documents, keyboard = get_documents_range(channels, offset)

    if not keyboard:
        keyboard = InlineKeyboardMarkup([])

    keyboard.inline_keyboard.extend(chunk((
        InlineKeyboardButton(d.get("name"), f"{channels.name}_info_{d.get('channel_id')}_{offset}")
        for d in documents), 2))

    fmt_channels = format_documents_list(documents.rewind(), lambda c:
        f"{can_send_icon(c.get('last_send'), c.get('delta'), c.get('scheduling').get('in_queue'), options('channels_delta'))}"
        f"{c.get('name')}\n"
        f"ID: {c.get('channel_id')}\n"
        f"Dal: {fmt_time(c.get('_id').generation_time)}"
    )

    await message.edit_text(channels_list.format(channels=fmt_channels), reply_markup=keyboard)

from pyrogram import filters
from pyrogram.types import CallbackQuery

from ..telegram import telegram


@telegram.on_callback_query(filters.create(lambda _, __, cq: cq.data == "dummy"))
def _dummy_btn_handler(_, callback_query: CallbackQuery):
    callback_query.answer()

from pyrogram import filters
from pyrogram.types import Message

from .mongo import admins


async def is_admin_filter(_, __, message: Message):
    return bool(not message.from_user or admins.find_one({"user_id": message.chat.id}))

is_admin = filters.create(is_admin_filter)


async def no_admins_filter(_, __, message: Message):
    return bool(not message.from_user or admins.count_documents({}) == 0)

no_admins = filters.create(no_admins_filter)

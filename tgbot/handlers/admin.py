from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.keyboards.admin_kb import admin_menu


async def admin_start(message: Message):
    await message.reply("Hello, admin!", reply_markup=admin_menu)


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["admin"], is_admin=True)

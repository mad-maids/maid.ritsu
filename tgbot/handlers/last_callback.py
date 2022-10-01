from aiogram.types import CallbackQuery
from aiogram import Dispatcher


async def lost(call: CallbackQuery):
    await call.answer('Time out')


def register_unhandled_call(dp: Dispatcher):
    dp.register_callback_query_handler(lost, state='*')

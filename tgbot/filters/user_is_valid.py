import typing

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from tgbot.models.students import Student


class IsValidUser(BoundFilter):

    key = "is_user_valid"

    def __init__(self, is_user_valid=typing.Optional[bool]):
        self.is_user_valid = is_user_valid

    async def check(self, obj, *args):
        session_maker = obj.bot.get('db')
        telegram_user: types.User = obj.from_user
        status = await Student.get_user_status(session_maker, telegram_user.id)
        if self.is_user_valid is True:
            return True if status == 1 else False
        else:
            return True

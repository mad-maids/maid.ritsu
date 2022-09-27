import typing

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from sqlalchemy.orm import sessionmaker
from tgbot.models.students import Student


class UserInDB(BoundFilter):
    key = "in_db"

    def __init__(self, in_db: typing.Optional[bool]):
        self.in_db = in_db

    async def check(self, obj, *args):
        if self.in_db is None:
            return True
        session_maker: sessionmaker = obj.bot.get('db')
        telegram_user: types.User = obj.from_user
        student = await Student.get_student(session_maker, telegram_user.id)

        data = dict(student=student)

        if student is None:
            if self.in_db is True:
                return False
            elif self.in_db is False:
                return True

        if student is not None:
            if self.in_db is True:
                return data
            elif self.in_db is False:
                return False

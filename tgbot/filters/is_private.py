import typing

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsPrivate(BoundFilter):

    key = "is_private"

    def __init__(self, is_private=typing.Optional[bool]):
        self.is_private = is_private

    async def check(self, obj, *args):
        chat: types.ChatType = obj.chat
        if self.is_private is None:
            return self.is_private and chat.is_private
        elif self.is_private is False:
            return not self.is_private and not chat.is_private
        else:
            return self.is_private and chat.is_private

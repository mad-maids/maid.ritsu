import typing

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsValidCar(BoundFilter):

    key = "is_valid_car"

    def __init__(self, is_valid_car=typing.Optional[bool]):
        self.is_valid_car = is_valid_car

    async def check(self, obj, *args):
        number: types.Message.text = obj.text
        if self.is_valid_car is True:
            return True if (x := len(number)) > 7 and x < 10 and number[:2].isnumeric() else False
        else:
            return True


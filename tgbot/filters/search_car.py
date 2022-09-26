import typing

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from sqlalchemy.orm import sessionmaker

from tgbot.models.cars import Car


class SearchCar(BoundFilter):

    key = "search_car"

    def __init__(self, search_car: typing.Optional[bool]):
        self.search_car = search_car

    async def check(self, obj, *args):
        if self.search_car is None or self.search_car is False:
            return True
        if self.search_car is True:
            session_maker: sessionmaker = obj.bot.get('db')
            query: types.InlineQuery = obj
            if (x := len(query.query)) > 7 and x < 10 and query.query[:2].isnumeric():
                cars = await Car.get_all_by_number_like(session_maker, query.query.upper().replace(" ", ""))
                data = dict(cars=cars)
                return data
            else:
                return False

from aiogram.dispatcher.filters.state import StatesGroup, State


class RegisterUser(StatesGroup):
    insert_car_number = State()
    insert_phone_number = State()


class DiscussionRoom(StatesGroup):
    join_room = State()
    in_room = State()


class Menu(StatesGroup):
    in_main_menu = State()

    start_chat = State()
    in_discussion = State()

    settings = State()
    car_settings = State()
    add_car = State()
    edit_car = State()

    phone_settings = State()

    feedback = State()
    about_us = State()



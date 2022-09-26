from aiogram import Dispatcher, types
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import sessionmaker

from tgbot.keyboards.inline import main_car_inline_keyboard, separate_car_inline_keyboard, car_callback, \
    main_menu_keyboard, settings_keyboard
from tgbot.misc.states import Menu
from tgbot.models.cars import Car
from tgbot.handlers.user_menu import settings


async def check_cars(call: CallbackQuery):
    cars = await Car.get_all_by_tg(call.bot.get("db"), call.from_user.id)
    for i in cars:
        await call.message.answer(f"🚗Your car is <code>{i.car_number}</code>",
                                  reply_markup=separate_car_inline_keyboard(i.car_number))
        await call.answer()
    await call.answer("🟡You don't seem to have any cars in the database. Please add a car", show_alert=True)


async def cars_settings(call: CallbackQuery):
    await call.message.edit_text("<b>Okay, what do you want to do with your cars?!</b>")
    await call.message.edit_reply_markup(main_car_inline_keyboard)
    await Menu.car_settings.set()


async def add_car(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("<b>Send me your car number please☺</b>")
    await Menu.add_car.set()


async def insert_card_number(msg: Message):
    session_maker: sessionmaker = msg.bot.get("db")
    car_num = msg.text.upper().replace(" ", "")
    await msg.reply("\n".join([
        "<b>🟢Nice! Your new number were recorded!</b>"
    ]), reply_markup=main_car_inline_keyboard)

    await Car.add_car(session_maker, car_number=car_num, owner=msg.from_user.id)
    await Menu.car_settings.set()


async def car_number_exist(msg: Message, ):
    await msg.answer(
        "<b>Looks like your car number is already taken, please contact admin via /report if necessary</b>",
        reply_markup=main_menu_keyboard)

    await Menu.in_main_menu.set()


async def delete_the_car(call: CallbackQuery, callback_data: dict):
    car_number = callback_data.get("number")
    if await Car.get_car(call.bot.get("db"), car_number) is None:
        await call.answer("🔴You don't own this car!", show_alert=True)
    else:
        await Car.delete_car(call.bot.get("db"), car_number)
        await call.answer('🟢Car was successfully deleted🗑', show_alert=True)
        await call.message.delete()
    await Menu.car_settings.set()


async def edit_the_car(call: CallbackQuery, callback_data: dict):
    car_number = callback_data.get("number")
    await call.answer()

    car_to_be_edited = await Car.get_car(call.bot.get("db"), car_number)
    if car_to_be_edited is None:
        await call.bot.send_message(call.from_user.id, "<b>You don't own this car 0_o</b>")
    else:
        await call.bot.send_message(call.from_user.id, "<b>I successfully deleted the car ^^</b>")
        await Car.delete_car(call.bot.get("db"), car_number)
    await Menu.edit_car()


async def update_card_number(msg: Message):
    session_maker: sessionmaker = msg.bot.get("db")
    car_num = msg.text.upper().replace(" ", "")
    await msg.reply("\n".join([
        "<b>We updated your car info</b>"
    ]), reply_markup=settings_keyboard)

    await Car.add_car(session_maker, car_number=car_num, owner=msg.from_user.id)
    await Menu.settings.set()


def user_settings_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(check_cars, state=Menu.car_settings, text='check_my_cars')
    dp.register_callback_query_handler(cars_settings, text="my_cars", state=Menu.settings, in_db=True)
    dp.register_callback_query_handler(settings, state=Menu.car_settings, text="close_car")
    dp.register_callback_query_handler(add_car,  text="add_car", state=Menu.car_settings)
    dp.register_message_handler(insert_card_number,  content_types=types.ContentType.TEXT, state=Menu.add_car,
                                car_in_db=False)
    dp.register_message_handler(car_number_exist,  content_types=types.ContentType.TEXT, state=Menu.add_car,
                                car_in_db=True)
    dp.register_callback_query_handler(delete_the_car, car_callback.filter(method="delete"), state=Menu.car_settings)
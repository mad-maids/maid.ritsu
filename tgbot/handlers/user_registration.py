import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker

from tgbot.filters.car_number_validator import IsValidCar
from tgbot.keyboards.inline import main_car_inline_keyboard, main_menu_keyboard
from tgbot.misc.states import RegisterUser, Menu
from tgbot.models.cars import Car
from tgbot.models.students import Student


async def user_start(msg: Message):
    # TODO: answer text
    last_send = await msg.answer("<b>Hello WIUTerian, my name is Ritsu, and I help you to find a car's owner</b>")
    await asyncio.sleep(1)
    await msg.bot.send_message(last_send.chat.id,
                               "\n".join(["<b>In order to use me, leave me some info about you </b>",
                                          "<b>First, send me your own car number</b>",
                                          "<b>Example:</b> <i>01777ААА</i>"]), )

    await RegisterUser.insert_car_number.set()


async def setting_car_number(msg: Message):
    # TODO: answer text
    await msg.answer("<b>Okay, what do you want to do with your cars?!</b>",
                     reply_markup=main_car_inline_keyboard)
    await Menu.car_settings.set()


async def register_car_number(msg: Message):
    # TODO: answer text
    session_maker: sessionmaker = msg.bot.get("db")
    car_num = msg.text.upper().replace(" ", "")
    await msg.reply('..fill this')
    await Student.create_student(session_maker, tg_id=msg.from_user.id)
    await Car.add_car(session_maker, car_number=car_num, owner=msg.from_user.id)
    await RegisterUser.insert_phone_number.set()


async def car_number_exist(msg: Message):
    # TODO: answer text
    await msg.answer(
        "<b>Looks like your car number is already taken, please contact admin via /report if necessary</b>",
        reply_markup=main_menu_keyboard)

    await Menu.in_main_menu.set()


async def register_phone_number(msg: Message, student: Student):
    session_maker = msg.bot.get("db")
    await msg.reply("\n".join(["<b> Good job ^_^, your contact is saved.</b>",
                               "<b>You can delete or edit it in settings, whenever you want.</b>"]),
                    reply_markup=main_menu_keyboard)
    updated_student = dict(tg_id=student.tg_id, first_name=msg.contact.first_name,
                           phone_number=msg.contact.phone_number)
    await student.update_client(session_maker, updated_student)

    await Menu.in_main_menu.set()


async def register_phone_number_forwarded(msg: Message):
    # TODO: answer text
    await msg.reply("\n".join(["<b> Looks like this phone number is not related to this account</b>",
                               "<b>I will not remember this one, but you can add another one in the settings</b>"]),
                    reply_markup=main_menu_keyboard)

    await Menu.in_main_menu.set()


async def cancel_phone_registration(msg: Message, state: FSMContext):
    await msg.answer(" ".join(["<b> Good, there is no need for me to know your phone number </b>",
                               "<b>to provide core functionality.</b>",
                               "<i>Hint: in settings, you are able to manage your data.</i>"]),
                     reply_markup=main_menu_keyboard)
    await state.finish()
    await Menu.in_main_menu.set()


async def tools(msg: Message):
    await msg.answer("🛠<b>  TOOLS  </b>", reply_markup=main_menu_keyboard)
    await Menu.in_main_menu.set()


async def user_restart(msg: Message, state=FSMContext):
    await state.finish()
    await msg.answer('🟢Everything was restarted🔄')


def user_registration_handlers(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], in_db=False)
    dp.register_message_handler(user_restart, commands=["start", "restart"], state="*")
    dp.register_message_handler(tools, commands='tools')

    dp.register_message_handler(register_car_number, IsValidCar(True), state=RegisterUser.insert_car_number,
                                car_in_db=False)

    dp.register_message_handler(car_number_exist, content_types=types.ContentType.TEXT,
                                state=RegisterUser.insert_car_number, car_in_db=True)

    dp.register_message_handler(cancel_phone_registration, commands="cancel",
                                state=RegisterUser.insert_phone_number, in_db=True)

    dp.register_message_handler(register_phone_number,
                                state=RegisterUser.insert_phone_number, content_types=types.ContentType.CONTACT,
                                in_db=True, is_forwarded=False)

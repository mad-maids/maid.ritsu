from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker

from tgbot.keyboards.inline import main_menu_keyboard, report_keyboad
from tgbot.misc.states import RegisterUser, Menu
from tgbot.models.cars import Car
from tgbot.models.students import Student


async def user_start(msg: Message):
    hello_text = f"π<b>Hello <i>{msg.from_user.first_name}</i></b>!\n\n" \
                 f"This bot will help you find the owner of a parked carπ\n" \
                 f"<b>Let's register together!</b>\n\n" \
                 f"πPlease, send me your car's number\n" \
                 f"<i>(Example: <b>01M777BA</b>)</i>"
    await msg.answer(hello_text)
    await RegisterUser.insert_car_number.set()


async def register_car_number(msg: Message, state: FSMContext):
    session_maker: sessionmaker = msg.bot.get("db")
    car_num = msg.text.upper().replace(" ", "")
    await msg.reply(f"π₯³ππππππππππππ ππ ππππ\n\n"
                    f"<i>π‘Additional cars and contact details\nare available via</i> /me"
                    f"\n\nπNow you can <b>search</b>, using /search")
    await Student.create_student(session_maker, tg_id=msg.from_user.id, first_name=msg.from_user.first_name)
    await Car.add_car(session_maker, car_number=car_num, owner=msg.from_user.id)
    await state.finish()


async def car_number_exist(msg: Message):
    await msg.reply(
        "<b>Looks like your car number is already taken, please contact admin via /report if necessary</b>")


async def report_handler(msg: Message):
    await msg.answer("Please choose, one of the options", reply_markup=report_keyboad)


async def main_menu(msg: Message):
    cars = await Car.get_all_by_tg(msg.bot.get("db"), msg.from_user.id)
    car = []
    for r in cars:
        car.append(r.car_number)
    await msg.answer(f"π€πππ¦π: <b>{msg.from_user.first_name}</b>\n"
                     f"ππππ«(π¬): <code>{'</code> <code>'.join(car)}</code>",
                     reply_markup=main_menu_keyboard)


async def user_not_in_db(msg: Message):
    await msg.answer("π‘Please, register first!\nUse /register")


async def user_restart(msg: Message, state: FSMContext):
    await state.finish()
    await msg.answer('π’Everything was restartedπ')


async def error_write_correct(msg: Message):
    await msg.answer('β Enter your data properly, please')


def user_registration_handlers(dp: Dispatcher):

    dp.register_message_handler(user_start, commands=["start", "register"], in_db=False,
                                is_not_banned=True, is_private=True)

    dp.register_message_handler(user_restart, commands=["restart", "start"], state=["*", None, ""], is_private=True)

    dp.register_message_handler(main_menu, commands=['me', 'profile'], in_db=True, is_private=True)

    dp.register_message_handler(user_not_in_db, commands=['me', 'profile'], in_db=False, is_private=True)

    dp.register_message_handler(register_car_number, state=RegisterUser.insert_car_number,
                                car_in_db=False, is_private=True, is_valid_car=True)

    dp.register_message_handler(car_number_exist, content_types=types.ContentType.TEXT,
                                state=RegisterUser.insert_car_number, car_in_db=True)

    # error handler Note: it also handles msgs from other modules
    dp.register_message_handler(error_write_correct,
                                state=[RegisterUser.insert_car_number,
                                       Menu.add_car,
                                       RegisterUser.insert_phone_number,
                                       Menu.search_number])

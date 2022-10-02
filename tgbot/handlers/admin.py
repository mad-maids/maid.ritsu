import asyncio

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.admin_kb import admin_menu, admin_cars_keyboard, admin_menu_call_data, admin_cars_call_data, \
    admin_drivers_keyboard, admin_driver_call_data
from tgbot.misc.states import AdminStates
from tgbot.models.cars import Car
from tgbot.models.students import Student


async def admin_start(message: Message):
    await message.reply("Hello, admin!", reply_markup=admin_menu)
    await AdminStates.in_admin_panel.set()


async def admin_cars(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Send me a number")
    await AdminStates.search_car.set()


async def admin_find_car_number(msg: Message):
    session_maker = msg.bot.get("db")
    cars = await Car.get_cars(session_maker=session_maker, car_number=msg.text)
    if len(cars )== 0:
        await msg.answer("Looks like car with this number doesn't exist")
    else:
        for c in cars:
            a = c.car_number
            status = "enabled"
            if c.status == 0:
                status = "disabled"
            await msg.answer(f'Order: {c.car_order}\n\n'
                             f'Car number: <code>{c.car_number}</code>\n\n'
                             f'Car owner id: <code>{c.owner}</code>\n\n'
                             f'Car status: <code>{status}</code>', reply_markup=admin_cars_keyboard(c.car_order))
            await asyncio.sleep(0.3)


async def disable_car(call: CallbackQuery, callback_data: dict, state: FSMContext):

    await Car.update_status_by_order(session_maker=call.bot.get("db"),
                                     order=int(callback_data.get("order")),
                                     status=dict(status=0))
    await call.answer("This car is disabled!")
    await call.message.delete()
    await state.finish()


async def enable_car(call: CallbackQuery, callback_data: dict, state: FSMContext):

    await Car.update_status_by_order(session_maker=call.bot.get("db"),
                                     order=int(callback_data.get("order")),
                                     status=dict(status=1))

    await call.answer("This car is enabled!")
    await call.message.delete()
    await state.finish()


async def admin_drivers(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Ok, send me a driver telegram_id")
    await AdminStates.search_driver.set()


async def admin_find_driver(msg: Message):

    student = await Student.get_any_student(session_maker=msg.bot.get("db"), tg_id=int(msg.text))
    if student is None:
        await msg.answer("Student with this id doesn't exist in our database")
    else:
        cars = await Car.get_all_by_tg(session_maker=msg.bot.get("db"), tg_id=student.tg_id)

        status = "active"
        if student.status == 0:
            status = "banned"

        car_nums = "\n\n"
        for c in cars:
            car_nums += "<code>" + str(c.car_order) + " " + c.car_number + "\n\n</code>"
        await msg.answer(f'Student id: <code>{student.tg_id}</code>\n\n'
                         f'Student first name: <code>{student.first_name}</code>\n\n'
                         f'Student phone number: <code>{student.phone_number}</code>\n\n'
                         f'Student status: <code>{status}</code>\n\n'
                         f'Cars: {car_nums}', reply_markup=admin_drivers_keyboard(student.tg_id))


async def ban_driver(call: CallbackQuery, callback_data: dict, state: FSMContext):
    student = Student(tg_id=int(callback_data.get("driver")))
    await student.update_client(session_maker=call.bot.get("db"),
                                updated_fields=dict(status=0))
    await call.answer("This car is disabled!")
    await call.message.delete()
    await state.finish()


async def unban_driver(call: CallbackQuery, callback_data: dict, state: FSMContext):
    student = Student(tg_id=int(callback_data.get("driver")))
    await student.update_client(session_maker=call.bot.get("db"),
                                updated_fields=dict(status=1))
    await call.answer("This car is disabled!")
    await call.message.delete()
    await state.finish()


async def hide(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    if state != "":
         await state.finish()


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, state=["*", ""], commands=["admin"], is_admin=True)

    # =======Cars======
    dp.register_callback_query_handler(admin_cars, admin_menu_call_data.filter(action="find_car"),
                                       state=AdminStates.in_admin_panel, is_admin=True)
    dp.register_message_handler(admin_find_car_number, state=AdminStates.search_car, is_admin=True)
    dp.register_callback_query_handler(disable_car, admin_cars_call_data.filter(action="disable"), state=["*", ""],
                                       is_admin=True)
    dp.register_callback_query_handler(enable_car, admin_cars_call_data.filter(action="enable"), state=["*", ""],
                                       is_admin=True)

    # ======Drivers======
    dp.register_callback_query_handler(admin_drivers,  admin_menu_call_data.filter(action="find_driver"),
                                       state=AdminStates.in_admin_panel, is_admin=True)
    dp.register_message_handler(admin_find_driver, state=AdminStates.search_driver, is_admin=True)
    dp.register_callback_query_handler(ban_driver, admin_driver_call_data.filter(action="ban_driver"),
                                       state=["*", ""], is_admin=True)
    dp.register_callback_query_handler(unban_driver, admin_driver_call_data.filter(action="unban_driver"),
                                       state=["*", ""], is_admin=True)
    # ========Universal button=======
    dp.register_callback_query_handler(hide, admin_menu_call_data.filter(action="hide"), state=["*", ""],
                                       is_admin=True)



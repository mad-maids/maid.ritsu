from aiogram import Dispatcher, types
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from sqlalchemy.orm import sessionmaker
from asyncio import sleep

from tgbot.keyboards.inline import main_car_inline_keyboard, separate_car_inline_keyboard, car_callback, \
 confirm_delete_kb, main_phone_inline_keyboard, delete_number_kb, back_inline_car, car_list
from tgbot.keyboards.reply import give_contact_kb

from tgbot.misc.states import Menu, RegisterUser
from tgbot.models.cars import Car
from tgbot.models.students import Student
from tgbot.handlers.user_menu import settings


# =========== CARS ==================
async def check_cars(call: CallbackQuery):
    cars = await Car.get_all_by_tg(call.bot.get("db"), call.from_user.id)
    c = []
    for i in cars:
        c.append(i.car_number)
    if c == list():
        await call.answer("🟡You don't seem to have any cars in the database. Please add a car", show_alert=True)
        return None
    await call.message.edit_text('🗒Here is your list of cars🚘', reply_markup=car_list(c))
    await call.answer()


async def cars_settings(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("<b>Okay, what do you want to do with your cars?</b>")
    await call.message.edit_reply_markup(main_car_inline_keyboard)
    await call.answer()


async def add_car(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("<b>Send me your car number please☺</b>", reply_markup=back_inline_car)
    await Menu.add_car.set()


async def insert_car_number(msg: Message, state: FSMContext):
    session_maker: sessionmaker = msg.bot.get("db")
    car_num = msg.text.upper().replace(" ", "")
    await msg.reply("\n".join([
        "<b>🟢Nice! Your new number was recorded!</b>"
    ]), reply_markup=main_car_inline_keyboard)
    await Car.add_car(session_maker, car_number=car_num, owner=msg.from_user.id)
    await state.finish()


async def car_number_exist(msg: Message, state: FSMContext):
    await msg.answer(
        "<b>Looks like your car number is already taken, please contact admin via /report if necessary</b>")
    await state.finish()


async def chosen_car_menu(call: CallbackQuery, callback_data: dict):
    car_number = callback_data.get("number")
    await call.message.edit_text(f'What are we going to do with <code>{car_number}</code>?',
                                 reply_markup=separate_car_inline_keyboard(car_number))
    await call.answer()


async def delete_the_car(call: CallbackQuery, callback_data: dict):
    car_number = callback_data.get("number")
    car = await Car.get_car(call.bot.get("db"), car_number)
    if car is None:
        await call.answer("🔴You don't own this car!", show_alert=True)
    else:
        await car.update_status_by_order(call.bot.get("db"), order=car.car_order, status=dict(status=0))
        await call.answer('🟢Car was successfully deleted🗑', show_alert=True)
        await call.message.delete()


# ===========    PHONE    ====================
async def phone_settings(call: CallbackQuery):
    await call.message.edit_text('<b>Okay, what do you want to do with your number?</b>')
    await call.message.edit_reply_markup(main_phone_inline_keyboard)
    await call.answer()


async def check_number(call: CallbackQuery):
    number = await Student.get_number_by_tg(call.bot.get("db"), call.from_user.id)
    try:
        assert number != "" and number is not None
        await call.message.edit_text(f"☎Your number: <code>{number}</code>",
                                     reply_markup=delete_number_kb)
        await call.answer()
    except AssertionError:
        await call.answer("🟡You don't seem to have a number in the database.", show_alert=True)


async def delete_number(call: CallbackQuery):
    session_maker: sessionmaker = call.bot.get("db")
    await Student.remove_number(session_maker, call.from_user.id)
    await call.answer('🟢Number was deleted successfully', show_alert=True)
    await phone_settings(call)


async def add_number(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer('📞Nice, send me your contact', reply_markup=give_contact_kb)
    await RegisterUser.insert_phone_number.set()


async def register_phone_number(msg: Message, student: Student, state: FSMContext):
    session_maker = msg.bot.get("db")
    updated_student = dict(tg_id=student.tg_id, first_name=msg.contact.first_name,
                           phone_number=msg.contact.phone_number)
    await student.update_client(session_maker, updated_student)
    await msg.reply('🥳Your contact is saved!\nYou can delete it whenever you want',
                    reply_markup=ReplyKeyboardRemove())
    await state.finish()
    await sleep(3)
    await msg.bot.delete_message(msg.chat.id, msg.message_id + 1)
    await msg.answer("<b>Okay, what do you want to do with your number?</b>",
                     reply_markup=main_phone_inline_keyboard)


async def cancel_phone_registration(msg: Message, state: FSMContext):
    await state.finish()
    await msg.answer("🤨it seems you've changed your mind", reply_markup=ReplyKeyboardRemove())
    await sleep(2)
    await msg.bot.delete_message(msg.chat.id, msg.message_id+1)
    await msg.answer("<b>Okay, what do you want to do with your number?</b>",
                     reply_markup=main_phone_inline_keyboard)


# =========== QUICK DELETE  ==================
async def confirm_delete(call: CallbackQuery):
    warning_text = f"<b>⚠BE CAREFUL</b>\n\n" \
                   f"<i>After deleting the data, you will not be able to use the Bot's services.</i>" \
                   f" <i>(You will need to register again🔄)</i>\n" \
                   f"\n<b>Are you sure?</b>"
    await call.message.edit_text(warning_text)
    await call.message.edit_reply_markup(confirm_delete_kb)
    await call.answer()


async def delete_all(call: CallbackQuery, state: FSMContext):
    session_maker: sessionmaker = call.bot.get("db")
    await Car.delete_all_by_tg(session_maker, tg_id=call.from_user.id)
    await Student.remove_number(session_maker, tg_id=call.from_user.id)
    await call.answer('🟢Everything was deleted successfully', show_alert=True)
    await call.message.delete()
    await state.finish()


def user_settings_handlers(dp: Dispatcher):
    # ============  CAR ============
    dp.register_callback_query_handler(check_cars, text='check_my_cars')
    dp.register_callback_query_handler(cars_settings, text="my_cars")
    dp.register_callback_query_handler(settings, text="close_car")
    dp.register_callback_query_handler(add_car, text="add_car")
    dp.register_message_handler(insert_car_number, content_types=types.ContentType.TEXT, state=Menu.add_car,
                                is_valid_car=True, car_in_db=False)
    dp.register_message_handler(car_number_exist, content_types=types.ContentType.TEXT, state=Menu.add_car,
                                car_in_db=True)
    dp.register_callback_query_handler(chosen_car_menu, car_callback.filter(method="open"))
    dp.register_callback_query_handler(delete_the_car, car_callback.filter(method="delete"))
    dp.register_callback_query_handler(check_cars, car_callback.filter(method='hide'))
    dp.register_callback_query_handler(cars_settings, state=Menu.add_car, text='to_settings')
    dp.register_callback_query_handler(cars_settings, text='car_list_back')

    #  ============ PHONE ============
    dp.register_callback_query_handler(phone_settings, text='my_phone')
    dp.register_callback_query_handler(settings, text='close_phone')
    dp.register_callback_query_handler(check_number, text='check_my_number')
    dp.register_callback_query_handler(delete_number, text='delete_number')
    dp.register_callback_query_handler(phone_settings, text='hide_number')
    dp.register_callback_query_handler(add_number, text='add_number')

    dp.register_message_handler(cancel_phone_registration,
                                state=RegisterUser.insert_phone_number,
                                text='🔙Back')

    dp.register_message_handler(register_phone_number,
                                state=RegisterUser.insert_phone_number, content_types=types.ContentType.CONTACT,
                                in_db=True, is_forwarded=False)
    # ============  DELETE ============
    dp.register_callback_query_handler(confirm_delete, text='delete_me')
    dp.register_callback_query_handler(delete_all, text='positive_delete')
    dp.register_callback_query_handler(settings, text='negative_delete')

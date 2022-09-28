from aiogram import Dispatcher, types
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from sqlalchemy.orm import sessionmaker
from asyncio import sleep

from tgbot.keyboards.inline import main_car_inline_keyboard, separate_car_inline_keyboard, car_callback, \
    main_menu_keyboard, confirm_delete_kb, main_phone_inline_keyboard, delete_number_kb, back_inline_car
from tgbot.keyboards.reply import give_contact_kb

from tgbot.misc.states import Menu, RegisterUser
from tgbot.models.cars import Car
from tgbot.models.students import Student
from tgbot.handlers.user_menu import settings


# =========== CARS ==================
async def check_cars(call: CallbackQuery):
    cars = await Car.get_all_by_tg(call.bot.get("db"), call.from_user.id)
    for i in cars:
        await call.message.answer(f"🚗Your car is <code>{i.car_number}</code>",
                                  reply_markup=separate_car_inline_keyboard(i.car_number))
        await call.answer()
    await call.answer("🟡You don't seem to have any cars in the database. Please add a car", show_alert=True)


async def cars_settings(call: CallbackQuery):
    await call.message.edit_text("<b>Okay, what do you want to do with your cars?</b>")
    await call.message.edit_reply_markup(main_car_inline_keyboard)
    await Menu.car_settings.set()
    await call.answer()


async def add_car(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("<b>Send me your car number please☺</b>", reply_markup=back_inline_car)
    await Menu.add_car.set()


async def insert_car_number(msg: Message):
    session_maker: sessionmaker = msg.bot.get("db")
    car_num = msg.text.upper().replace(" ", "")
    await msg.reply("\n".join([
        "<b>🟢Nice! Your new number was recorded!</b>"
    ]), reply_markup=main_car_inline_keyboard)

    await Car.add_car(session_maker, car_number=car_num, owner=msg.from_user.id)
    await Menu.car_settings.set()


async def car_number_exist(msg: Message, ):
    await msg.answer(
        "<b>Looks like your car number is already taken, please contact admin via /report if necessary</b>",
        reply_markup=main_menu_keyboard)


async def delete_the_car(call: CallbackQuery, callback_data: dict):
    car_number = callback_data.get("number")
    if await Car.get_car(call.bot.get("db"), car_number) is None:
        await call.answer("🔴You don't own this car!", show_alert=True)
    else:
        await Car.delete_car(call.bot.get("db"), car_number)
        await call.answer('🟢Car was successfully deleted🗑', show_alert=True)
        await call.message.delete()
    await Menu.car_settings.set()


# ===========    PHONE    ====================
async def phone_settings(call: CallbackQuery):
    await Menu.phone_settings.set()
    await call.message.edit_text('<b>Okay, what do you want to do with your number?</b>')
    await call.message.edit_reply_markup(main_phone_inline_keyboard)
    await call.answer()


async def check_number(call: CallbackQuery):
    number = await Student.get_number_by_tg(call.bot.get("db"), call.from_user.id)
    try:
        assert number != "" and number is not None
        await call.message.answer(f"☎Your number: {number}",
                                  reply_markup=delete_number_kb)
        await call.answer()
    except AssertionError:
        await call.answer("🟡You don't seem to have a number in the database.", show_alert=True)


async def delete_number(call: CallbackQuery):
    session_maker: sessionmaker = call.bot.get("db")
    await Student.remove_number(session_maker, call.from_user.id)
    await call.answer('🟢Number was deleted successfully')
    await hide_sub_menu(call)


async def add_number(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer('📞Nice, send me your contact', reply_markup=give_contact_kb)
    await RegisterUser.insert_phone_number.set()


async def register_phone_number(msg: Message, student: Student):
    session_maker = msg.bot.get("db")
    updated_student = dict(tg_id=student.tg_id, first_name=msg.contact.first_name,
                           phone_number=msg.contact.phone_number)
    await student.update_client(session_maker, updated_student)
    await msg.reply('🥳Your contact is saved!\nYou can delete it whenever you want',
                    reply_markup=ReplyKeyboardRemove())
    await sleep(3)
    await msg.bot.delete_message(msg.chat.id, msg.message_id + 1)
    await Menu.phone_settings.set()
    await msg.answer("<b>Okay, what do you want to do with your number?</b>",
                     reply_markup=main_phone_inline_keyboard)


async def cancel_phone_registration(msg: Message, state: FSMContext):
    await state.finish()
    await Menu.phone_settings.set()
    await msg.answer("🤨it seems you've changed your mind", reply_markup=ReplyKeyboardRemove())
    await sleep(2)
    await msg.bot.delete_message(msg.chat.id, msg.message_id+1)
    await msg.answer("<b>Okay, what do you want to do with your number?</b>",
                     reply_markup=main_phone_inline_keyboard)


# =========== QUICK DELETE  ==================
async def hide_sub_menu(call: CallbackQuery):
    await call.message.delete()


async def confirm_delete(call: CallbackQuery):
    warning_text = f"<b>⚠BE CAREFUL</b>\n\n" \
                   f"<i>After deleting the data, you will not be able to use the Bot's services.</i>" \
                   f" <i>(You will need to register again🔄)</i>\n" \
                   f"\n<b>Are you sure?</b>"
    await call.message.edit_text(warning_text)
    await call.message.edit_reply_markup(confirm_delete_kb)
    await call.answer()


async def delete_all(call: CallbackQuery, state=FSMContext):
    session_maker: sessionmaker = call.bot.get("db")
    await Car.delete_all_by_tg(session_maker, tg_id=call.from_user.id)
    await Student.remove_number(session_maker, tg_id=call.from_user.id)
    await call.answer('🟢Everything was deleted successfully', show_alert=True)
    await call.message.delete()
    await state.finish()


def user_settings_handlers(dp: Dispatcher):
    # ============  CAR ============
    dp.register_callback_query_handler(check_cars, state=Menu.car_settings, text='check_my_cars')
    dp.register_callback_query_handler(cars_settings, text="my_cars", state=Menu.settings)
    dp.register_callback_query_handler(settings, state=Menu.car_settings, text="close_car")
    dp.register_callback_query_handler(add_car, text="add_car", state=Menu.car_settings)
    dp.register_message_handler(insert_car_number, content_types=types.ContentType.TEXT, state=Menu.add_car,
                                car_in_db=False, is_valid_car=True)
    dp.register_message_handler(car_number_exist, content_types=types.ContentType.TEXT, state=Menu.add_car,
                                car_in_db=True)
    dp.register_callback_query_handler(delete_the_car, car_callback.filter(method="delete"), state=Menu.car_settings)
    dp.register_callback_query_handler(hide_sub_menu, car_callback.filter(method='hide'), state=Menu.car_settings)
    dp.register_callback_query_handler(cars_settings, state=Menu.add_car, text='to_settings')
    #  ============ PHONE ============
    dp.register_callback_query_handler(phone_settings, text='my_phone', state=Menu.settings)
    dp.register_callback_query_handler(settings, text='close_phone', state=Menu.phone_settings)
    dp.register_callback_query_handler(check_number, state=Menu.phone_settings, text='check_my_number')
    dp.register_callback_query_handler(delete_number, state=Menu.phone_settings, text='delete_number')
    dp.register_callback_query_handler(hide_sub_menu, state=Menu.phone_settings, text='hide_number')
    dp.register_callback_query_handler(add_number, state=Menu.phone_settings, text='add_number')
    dp.register_message_handler(cancel_phone_registration, state=RegisterUser.insert_phone_number,
                                text='🔙Back')
    dp.register_message_handler(register_phone_number,
                                state=RegisterUser.insert_phone_number, content_types=types.ContentType.CONTACT,
                                in_db=True, is_forwarded=False)
    # ============  DELETE ============
    dp.register_callback_query_handler(confirm_delete, state=Menu.settings, text='delete_me')
    dp.register_callback_query_handler(delete_all, state=Menu.settings, text='positive_delete')
    dp.register_callback_query_handler(settings, state=Menu.settings, text='negative_delete')

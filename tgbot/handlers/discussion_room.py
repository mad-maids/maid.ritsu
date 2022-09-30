from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.config import Config
from tgbot.keyboards.inline import found_driver_keyboard, car_callback, back_inline_car, feedback_keyboard, \
    found_driver_keyboard_extra, on_my_way, on_my_way_extra, notify_callback, ignore_callback
from tgbot.misc.states import Menu
from tgbot.models.cars import Car
from tgbot.models.students import Student


# ============= FEEDBACK =====================
async def feedback_discussion(msg: Message):
    config: Config = msg.bot.get("config")
    await msg.bot.send_message(
        config.tg_bot.admins_group[0],
        "".join([f"<b>From user: <a href='tg://user?id={msg.from_user.id}'>{msg.from_user.first_name}</a></b>\n\n",
                 f"<i>{msg.text}</i>"],
                ))


# ============= SEARCH =====================
async def start_search(msg: Message):
    await Menu.search_number.set()
    await msg.answer('👮‍♂Alright, please <b>send the number of the car</b> that prevents you from leaving the '
                     'parking lot', reply_markup=back_inline_car)
    # TODO: add a timer to auto-delete it


async def search_owner(msg: Message, cars: [Car]):
    for car in cars:
        session_maker = msg.bot.get("db")
        owner_id = await Car.get_owner_by_car(session_maker, car.car_number)
        number = await Student.get_number_by_tg(session_maker, owner_id)
        phone = f"📞𝐏𝐡𝐨𝐧𝐞 : <code>{number}</code>" if number is not None else ''
        await msg.answer(
                         f"🔹𝐓𝐡𝐞 𝐨𝐰𝐧𝐞𝐫 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐟𝐨𝐮𝐧𝐝\n"
                         f"🚘𝐂𝐚𝐫 : <code>{msg.text.upper()}</code>\n"
                         f"{phone}",
                         reply_markup=found_driver_keyboard(car.car_number))
        return None
    else:
        await msg.answer('🔍The owner was not found😕')


async def stop_search(call: CallbackQuery, state=FSMContext):
    await state.finish()
    await call.answer('🔻Search has stopped')
    await call.message.delete()


# ============= CHAT =====================

async def on_my_way_respond(call: CallbackQuery, callback_data: dict):
    r_car_number = callback_data.get("number")
    tg_id = callback_data.get("tg_id")

    respond_text = f"👤The owner is already heading to the car"
    await call.answer("🔔We have informed the requester")
    await call.message.edit_reply_markup(on_my_way_extra(r_car_number))
    await call.message.bot.send_message(tg_id, respond_text)


async def notify_user(call: CallbackQuery, callback_data: dict, state=FSMContext):
    car_number = callback_data.get("number")

    session_maker = call.bot.get("db")
    car_owner = await Car.get_car(session_maker, car_number)
    requester = await Car.get_car_by_tg(session_maker, call.from_user.id)

    await call.message.edit_reply_markup(found_driver_keyboard_extra(car_number))

    notify_text = f"👋Hello!\n" \
                  f"❗YOUR CAR <b>PREVENTS</b> ANOTHER CAR\n" \
                  f"❕FROM LEAVING THE PARKING LOT\n" \
                  f"\n" \
                  f"🙏Please come to your car\n" \
                  f"👤Request from: <code>{requester.car_number.upper()}</code>"
    await call.message.bot.send_message(car_owner.owner, notify_text, disable_web_page_preview=True,
                                        reply_markup=on_my_way(call.from_user.id, requester.car_number))

    await state.storage.set_state(chat=car_owner.owner, user=car_owner.owner, state=Menu.search_number)

    await call.answer('👮‍♂We have notified her/him🛎', show_alert=True)


async def ignore_request(call: CallbackQuery, callback_data: dict, state=FSMContext):
    partner = callback_data.get("tg_id")
    await call.bot.send_message(partner, "💬The owner chose not to answer you🙁")
    await state.storage.finish(chat=partner, user=partner)

    await call.answer('You ignored them🫡')
    await state.finish()
    await call.message.delete()


# ============= CHAT =====================
async def cancel_searching(call: CallbackQuery, state=FSMContext):
    await call.message.answer('🔍Search has stopped🛑')
    await call.answer()
    await state.finish()
    await call.message.delete()


async def cancel_chatting(call: CallbackQuery, state=FSMContext):
    data = await state.get_data()
    partner = data.get("partner")
    await call.bot.send_message(partner, "💬The dialogue was finished🛑")
    await state.storage.finish_state(chat=partner, user=partner)

    await call.message.answer('💬The dialogue was finished🛑')
    await call.answer()
    await call.message.delete()
    await state.finish()


async def start_chatting(call: CallbackQuery, callback_data: dict, state: FSMContext):
    car_number = callback_data.get("number")
    print(f'chat was started {callback_data.get("number")}')

    session_maker = call.bot.get("db")
    requester = await Car.get_car_by_tg(session_maker, call.from_user.id)

    start_text = f"🟢<b>The dialogue has begun</b>💬\n" \
                 f"<i>You can write messages and they will be\nsent to the owner of the car</i>"

    start_text_r = f"🟢<b>Someone (<code>{requester.car_number}</code>) started dialogue with you</b>💬\n" \
                   f"<i>You can write messages and they will be\nsent to the owner of the car</i>"
    # who called
    await call.message.edit_text(start_text)
    await call.message.edit_reply_markup(feedback_keyboard)

    # owner
    car_owner = await Car.get_car(session_maker, car_number)

    await call.message.bot.send_message(car_owner.owner, start_text_r, reply_markup=feedback_keyboard)

    await state.storage.set_state(chat=car_owner.owner, user=car_owner.owner, state=Menu.start_chat.state)
    await state.storage.set_data(chat=car_owner.owner, user=car_owner.owner, data=dict(partner=call.from_user.id))

    await Menu.start_chat.set()

    await state.update_data(dict(partner=car_owner.owner))


async def send_message(msg: Message, state: FSMContext):
    data = await state.get_data()
    partner = data.get("partner")

    partner_state = await state.storage.get_state(chat=partner, user=partner)
    partner_data = await state.storage.get_data(chat=partner, user=partner)
    if partner_state == Menu.start_chat.state:
        if partner_data.get("partner") == msg.from_user.id:
            await msg.bot.send_message(data.get("partner"),
                                       f"👤<b>Interlocutor</b>:\n\n<i>{msg.text}</i>\n"
                                       f"\n<b>[ /finish to end the dialog ]</b>")
        else:
            await msg.answer("This driver is chatting with another car driver, please try later👀")
            await state.finish()

    else:
        await msg.answer("<b>🔚Your Partner decided to end conversation😕</b>")
        await state.finish()


async def finish(msg: Message, state=FSMContext):
    data = await state.get_data()
    partner = data.get("partner")
    await msg.bot.send_message(partner, "💬The dialogue was finished🛑")
    await state.storage.finish(chat=partner, user=partner)

    await msg.answer('💬The dialogue was finished🛑')
    await msg.delete()
    await state.finish()


# ============= ERRORS =====================
async def error_late_start(call: CallbackQuery):
    await call.answer('🟡The chat has already started')


def discussion_handlers(dp: Dispatcher):
    # ========= FEEDBACK ==========
    dp.register_message_handler(feedback_discussion, state=Menu.feedback)

    # ========= SEARCH ==========
    dp.register_message_handler(start_search, commands='search', is_user_valid=True)

    dp.register_message_handler(search_owner, search_car=True, state=Menu.search_number)
    dp.register_callback_query_handler(stop_search, state=Menu.search_number, text='to_settings')
    dp.register_message_handler(finish, commands="finish", state=[Menu.start_chat])

    # ========= Notify ==========
    dp.register_callback_query_handler(notify_user, car_callback.filter(method="notify"), state=Menu.search_number)
    dp.register_callback_query_handler(on_my_way_respond, notify_callback.filter(method='on_my_way'),
                                       state=Menu.search_number)

    dp.register_callback_query_handler(ignore_request, ignore_callback.filter(method='ignore'),
                                       state=Menu.search_number)
    # ========= CHAT ==========
    dp.register_callback_query_handler(cancel_chatting, text=["back_to_menu"],
                                       state=Menu.start_chat)
    dp.register_callback_query_handler(cancel_searching, text="cancel_chatting",
                                       state=Menu.search_number)

    dp.register_callback_query_handler(start_chatting, car_callback.filter(method="enter_room"),
                                       state=Menu.search_number)
    dp.register_message_handler(send_message, state=Menu.start_chat)
    # ======== ERRORS =========
    dp.register_callback_query_handler(error_late_start, car_callback.filter(method="enter_room"),
                                       state=Menu.start_chat)

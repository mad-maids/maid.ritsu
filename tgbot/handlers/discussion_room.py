from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.config import Config
from tgbot.keyboards.inline import found_driver_keyboard, car_callback, back_inline_car
from tgbot.misc.states import Menu
from tgbot.models.cars import Car
from tgbot.models.students import Student

from tgbot.keyboards.inline import feedback_keyboard


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


async def notify_user(call: CallbackQuery):
    # TODO: add an quick notify button's functionality
    pass


async def cancel_chatting(call: CallbackQuery, state=FSMContext):
    await call.answer()
    await call.message.answer('🔍Search has stopped🛑')
    await call.message.delete()
    await state.finish()


async def start_chatting(call: CallbackQuery, callback_data: dict, state: FSMContext):
    car_number = callback_data.get("number")
    print(f'chat was started {callback_data.get("number")}')

    await call.message.edit_text(f"🟢<b>The dialogue has begun</b>💬\n"
                                 f"<i>You can write messages and they will be\nsent to the owner of the car</i>")
    await call.message.edit_reply_markup(feedback_keyboard)
    car_owner = await Car.get_car(call.bot.get("db"), car_number)

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
            await msg.bot.send_message(data.get("partner"), f"\n{msg.text}\n<i>[ /finish to end the dialog ]</i>")
        else:
            await msg.answer("This driver is chatting with another car driver, please try later👀")
            await state.finish()

    else:
        await msg.answer("<b>🔚Your Partner decided to end conversation😕</b>")
        await state.finish()


async def finish(msg: Message, state=FSMContext):
    await msg.delete()
    await msg.answer('💬The dialogue was finished🛑')
    await state.finish()


def discussion_handlers(dp: Dispatcher):
    # ========= FEEDBACK ==========
    dp.register_message_handler(feedback_discussion, state=Menu.feedback)

    # ========= SEARCH ==========
    dp.register_message_handler(start_search, commands='search', in_db=True)
    dp.register_message_handler(search_owner, search_car=True, state=Menu.search_number)
    dp.register_callback_query_handler(stop_search, state=Menu.search_number, text='to_settings')
    dp.register_message_handler(finish, commands="finish", state=[Menu.start_chat])

    # ========= CHAT ==========
    dp.register_callback_query_handler(notify_user, car_callback.filter(method="notify"), state=Menu.search_number)
    dp.register_callback_query_handler(cancel_chatting, text=["cancel_chatting", "back_to_menu"],
                                       state=[Menu.start_chat, Menu.search_number])
    dp.register_callback_query_handler(start_chatting, car_callback.filter(method="enter_room"),
                                       state=Menu.search_number)
    dp.register_message_handler(send_message, state=Menu.start_chat)

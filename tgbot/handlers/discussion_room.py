from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineQueryResultArticle, InlineQuery, InputTextMessageContent, CallbackQuery

from tgbot.config import Config
from tgbot.keyboards.inline import found_driver_keyboard, car_callback, main_menu_keyboard
from tgbot.misc.states import Menu
from tgbot.models.cars import Car


async def feedback_discussion(msg: Message):
    config: Config = msg.bot.get("config")

    await msg.bot.send_message(
        config.tg_bot.admins_group[0],
        "".join([f"<b>From user:\n <a href='tg://user?id={msg.from_user.id}'>{msg.from_user.first_name}</a></b>\n\n",
                 f"<i>{msg.text}</i>"],
                ))


async def search_owner(query: InlineQuery, cars: [Car]):
    car_numbers = []

    for car in cars:
        car_numbers.append(InlineQueryResultArticle(
            id=f"{car.car_number}",
            title=f"{car.car_number}",
            reply_markup=found_driver_keyboard(car.car_number),
            input_message_content=InputTextMessageContent(
                message_text=f"<b>{car.car_number}</b>",
            )))

    await query.answer(
        results=car_numbers,
        cache_time=2)


async def cancel_chatting(call: CallbackQuery):
    await call.answer()
    await call.message.answer("main menu", reply_markup=main_menu_keyboard)
    await Menu.in_main_menu.set()


async def start_chatting(call: CallbackQuery, callback_data: dict, state: FSMContext):
    car_number = callback_data.get("number")
    await call.bot.send_message(call.from_user.id,
                                "<b>You can write now, all messages will be delivered to the car owner.</b>\n write "
                                "/finish to end a chat",
                                )
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
            await msg.bot.send_message(data.get("partner"), msg.text + "\n send /finish to end dialog")
        else:
            await msg.answer("This driver is chatting with another car driver, please try later",
                             reply_markup=main_menu_keyboard)
            # TODO: add extra inline keyboards, with hold and return to menu buttons, if partner is busy
            await Menu.in_main_menu.set()

    else:
        await msg.answer("<b>Your Partner decided to end conversation</b>", reply_markup=main_menu_keyboard)
        await Menu.in_main_menu.set()


def discussion_handlers(dp: Dispatcher):
    dp.register_message_handler(feedback_discussion, state=Menu.feedback)
    dp.register_inline_handler(search_owner, search_car=True, state=Menu.in_main_menu)
    dp.register_callback_query_handler(cancel_chatting, text="cancel_chatting", state=Menu.start_chat)
    dp.register_callback_query_handler(start_chatting, car_callback.filter(method="enter_room"),
                                       state=Menu.in_main_menu)
    dp.register_message_handler(send_message, state=Menu.start_chat)

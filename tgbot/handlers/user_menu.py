from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.inline import settings_keyboard, feedback_keyboard, about_us_keyboard, main_menu_keyboard
from tgbot.misc.states import Menu
from tgbot.models.cars import Car


async def settings(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "".join(["<b> In this section, you can manage</b>"
                 "<b> information that related to you.</b>"]))
    await call.message.edit_reply_markup(settings_keyboard)
    await Menu.settings.set()


async def feedback(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("".join(["<b>Now, everything you write here will be forwarded ",
                                       "to admins. Then, they can contact you directly or via me if needed</b>"
                                       ]),
                              reply_markup=feedback_keyboard
                              )
    await Menu.feedback.set()


async def about_us(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(f"𝐖𝐈𝐔𝐓 𝐏𝐚𝐫𝐤𝐢𝐧𝐠 𝐛𝐨𝐭\n"
                              f"This bot exists thankfully for those who contributed\n"
                              f"this project, and they are:\n\n"
                              f"👨‍💻<a href='https://github.com/Azizbek-B'>Azizbek</a> (Co-Creator, Maintainer)\n"
                              f"🕵️‍♂<a href='https://t.me/muminovbob'>Bobomurod</a> (Co-Creator, Maintainer)\n"
                              f"👩‍🚀<a href='https://github.com/uwussimo'>UwUssimo</a> (Core Contributor)\n\n"
                              f"Copyright © 2022 <a href='https://github.com/mad-maids'>Mad Maids</a>",
                              reply_markup=about_us_keyboard,
                              disable_web_page_preview=True)
    await Menu.about_us.set()


async def exit_to_menu(call: CallbackQuery):
    await call.message.delete()
    cars = await Car.get_all_by_tg(call.bot.get("db"), call.from_user.id)
    car = []
    for r in cars:
        car.append(r.car_number)
    await call.message.answer(f"👤𝐍𝐚𝐦𝐞: <b>{call.from_user.first_name}</b>\n"
                              f"🚙𝐂𝐚𝐫(𝐬): <code>{' '.join(car)}</code>",
                              reply_markup=main_menu_keyboard)
    await Menu.in_main_menu.set()


async def close_menu(call: CallbackQuery, state=FSMContext):
    await state.finish()
    await call.answer()
    await call.message.delete()


def user_menu_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(settings, text="settings", state=Menu.in_main_menu, in_db=True)
    dp.register_callback_query_handler(about_us, text="about", state=Menu.in_main_menu, in_db=True)

    dp.register_callback_query_handler(feedback, text="feedback", state=Menu.in_main_menu, in_db=True)
    dp.register_callback_query_handler(exit_to_menu, text="back_to_menu", state="*")
    dp.register_callback_query_handler(close_menu, state=Menu.in_main_menu, text='hide_menu')

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

main_car_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🕵️‍♂️Check my cars", callback_data='check_my_cars')],
    [InlineKeyboardButton(text="➕Add a car", callback_data="add_car")],
    [InlineKeyboardButton(text="🔙Back", callback_data="close_car")]
])

car_callback = CallbackData("car", "method", "number")
notify_callback = CallbackData("car", "method", "number", 'tg_id')
ignore_callback = CallbackData("car", "method", 'tg_id')


def found_driver_keyboard(car_number: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔔Notify them',
                              callback_data=car_callback.new(method="notify", number=car_number))],
        [InlineKeyboardButton(text="💬Start chatting",
                              callback_data=car_callback.new(method="enter_room", number=car_number)),
         InlineKeyboardButton(text="◀Cancel",
                              callback_data="cancel_chatting")]])
    return keyboard


def found_driver_keyboard_extra(car_number: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬Start chatting",
                              callback_data=car_callback.new(method="enter_room", number=car_number)),
         InlineKeyboardButton(text="◀Cancel",
                              callback_data="cancel_chatting")]])
    return keyboard


def separate_car_inline_keyboard(car_number: str):
    temp_inline_keyboard = InlineKeyboardMarkup(row_width=1)
    temp_inline_keyboard.add(
        InlineKeyboardButton(text="🗑Delete this car",
                             callback_data=car_callback.new(method="delete", number=car_number)),
        InlineKeyboardButton(text='🔙Back', callback_data=car_callback.new(method="hide", number=car_number)))
    return temp_inline_keyboard


def car_list(user_numbers: list):
    temp_inline_keyboard = InlineKeyboardMarkup(row_width=1)
    for number in user_numbers:
        temp_inline_keyboard.add(
            InlineKeyboardButton(text=number, callback_data=car_callback.new(method="open", number=number))
        )
    temp_inline_keyboard.add(
        InlineKeyboardButton(text='🔙Back', callback_data="car_list_back"))
    return temp_inline_keyboard


main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
                     [InlineKeyboardButton(text="Settings⚙️", callback_data="settings")],
                     [InlineKeyboardButton(text="About us™️", callback_data="about"),
                      InlineKeyboardButton(text="Feedback🛎", callback_data="feedback")],
                     [InlineKeyboardButton(text='Close❌', callback_data='hide_menu')]],
    resize_keyboard=True)

settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🚗Cars", callback_data="my_cars")],
    [InlineKeyboardButton(text="📞Contacts", callback_data="my_phone")],
    [InlineKeyboardButton(text="🔙Back", callback_data="back_to_menu"),
     InlineKeyboardButton(text='🗑Delete everything', callback_data='delete_me')]],
    resize_keyboard=True)

about_us_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙Back", callback_data="back_to_menu")]],
    resize_keyboard=True
)

feedback_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏁Finish", callback_data="back_to_menu")]],
    resize_keyboard=True
)

feedback_keyboard_after = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏁Finish", callback_data="back_to_menu_after")]],
    resize_keyboard=True
)


confirm_delete_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🗑Yes, I want to clear my data', callback_data='positive_delete')],
    [InlineKeyboardButton(text='🔙Back', callback_data='negative_delete')]
])


main_phone_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📞My number", callback_data='check_my_number')],
    [InlineKeyboardButton(text="➕Set a number", callback_data="add_number")],
    [InlineKeyboardButton(text="🔙Back", callback_data="close_phone")]
])

delete_number_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🗑Delete", callback_data='delete_number')],
    [InlineKeyboardButton(text='🔙Back', callback_data='hide_number')]
])

back_inline_car = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙Back', callback_data='to_settings')]
])


def on_my_way(tg_id, car_number):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='👌On my way',
                              callback_data=notify_callback.new(method="on_my_way", tg_id=tg_id, number=car_number))],
        [InlineKeyboardButton(text="💬Start chatting",
                              callback_data=car_callback.new(method="enter_room", number=car_number)),
         InlineKeyboardButton(text='🚫Ignore',
                              callback_data=ignore_callback.new(method="ignore", tg_id=tg_id))]])
    return keyboard


def on_my_way_extra(car_number):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬Start chatting",
                              callback_data=car_callback.new(method="enter_room", number=car_number))]])
    return keyboard


report_callback_data = CallbackData("report", "description", "car")

scam_button = InlineKeyboardButton(
    text="Report scam",
    callback_data=report_callback_data.new(description="report", car="car")
)

abuse_button = InlineKeyboardButton(
    text="Report abuse",
    callback_data=report_callback_data.new(description="abuse", car="car")
)

stolen_car_button = InlineKeyboardButton(
    text="Report stolen car number",
    callback_data=report_callback_data.new(description="stolen_car", car="car")
)

other_report_button = InlineKeyboardButton(
    text="Another issue",
    callback_data=report_callback_data.new(description="other", car="car")
)
report_keyboad = InlineKeyboardMarkup(resize_keyboard=True)
report_keyboad.add(stolen_car_button)
report_keyboad.add(scam_button)
report_keyboad.add(abuse_button)
report_keyboad.add(other_report_button)

report_agreement_callback_data = CallbackData("report_confirmation", "answer")

report_agreement_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Yes✅", callback_data=report_agreement_callback_data.new(answer="yes"))
    ],
    [
        InlineKeyboardButton(text="No❌", callback_data=report_agreement_callback_data.new(answer="no"))
    ]],
    resize_keyboard=True)

discussion_finish_call_data = CallbackData("finish_chat", "action")

discussion_finish_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Report📣", callback_data=discussion_finish_call_data.new(action="report"))
    ],
    [
        InlineKeyboardButton(text="Close🚫", callback_data=discussion_finish_call_data.new(action="close"))
    ]],
    resize_keyboard=True)

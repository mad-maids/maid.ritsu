from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

main_car_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🕵️‍♂️Check my cars", callback_data='check_my_cars')],
    [InlineKeyboardButton(text="➕Add a car", callback_data="add_car")],
    [InlineKeyboardButton(text="🔙Back", callback_data="close_car")]
])

car_callback = CallbackData("car", "method", "number")


def found_driver_keyboard(car_number: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔔Notify them',
                              callback_data=car_callback.new(method="notify", number=car_number))],
        [InlineKeyboardButton(text="💬Start chatting",
                              callback_data=car_callback.new(method="enter_room", number=car_number)),
         InlineKeyboardButton(text="◀Cancel",
                              callback_data="cancel_chatting")]])
    return keyboard


def separate_car_inline_keyboard(car_number: str):
    temp_inline_keyboard = InlineKeyboardMarkup(row_width=1)
    temp_inline_keyboard.add(
        InlineKeyboardButton(text='👁Hide', callback_data=car_callback.new(method="hide", number=car_number)),
        InlineKeyboardButton(text="🗑Delete this car",
                             callback_data=car_callback.new(method="delete", number=car_number)))
    return temp_inline_keyboard


main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
                     [InlineKeyboardButton(text="Settings⚙️", callback_data="settings")],
                     [InlineKeyboardButton(text="About us™️", callback_data="about"),
                      InlineKeyboardButton(text="Feedback🛎", callback_data="feedback")],
                     [InlineKeyboardButton(text='👁Hide', callback_data='hide_menu')]],
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
    [InlineKeyboardButton(text='👁Hide', callback_data='hide_number')],
    [InlineKeyboardButton(text="🗑Delete", callback_data='delete_number')]
])

back_inline_car = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙Back', callback_data='to_settings')]
])

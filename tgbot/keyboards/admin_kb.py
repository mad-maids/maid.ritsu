from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

admin_menu_call_data = CallbackData("menu", "action")


admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='💬Start chat', callback_data=admin_menu_call_data.new(action="start_chat"))
    ],
    [
        InlineKeyboardButton(text='🔎Find a car', callback_data=admin_menu_call_data.new(action="find_car")),
        InlineKeyboardButton(text='🔎Find a driver', callback_data=admin_menu_call_data.new(action="find_driver"))

    ],
    [
        InlineKeyboardButton(text='👁Hide', callback_data=admin_menu_call_data.new(action="hide"))
    ]
],
    resize_keyboard=True)

admin_cars_call_data = CallbackData("menu", "action", "order")


def admin_cars_keyboard(order: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='🔒Disable', callback_data=admin_cars_call_data.new(
                action="disable", order=order)),
            InlineKeyboardButton(text='🔓Enable', callback_data=admin_cars_call_data.new(
                action="enable", order=order))
        ]
        ,
        [
            InlineKeyboardButton(text='🗑Delete', callback_data=admin_cars_call_data.new(
                action="delete", order=order))
        ],
        [
            InlineKeyboardButton(text='👁Hide', callback_data=admin_menu_call_data.new(action="hide"))
        ]
    ], resize_keyboard=True)


admin_driver_call_data = CallbackData("drivers", "action", "driver")


def admin_drivers_keyboard(driver_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='🔒Ban', callback_data=admin_driver_call_data.new(action="ban_driver",
                                                                                       driver=driver_id)),
            InlineKeyboardButton(text='🔓Unban', callback_data=admin_driver_call_data.new(action="unban_driver",
                                                                                         driver=driver_id))
        ],
        [
            InlineKeyboardButton(text='👁Hide', callback_data=admin_menu_call_data.new(action="hide"))
        ]
    ], resize_keyboard=True)


def admin_feedback_keyboard(driver_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬Start chat",
                              callback_data=admin_driver_call_data.new(action="start_discussion", driver=driver_id)),
         InlineKeyboardButton(text="⏳Answer later",
                              callback_data=admin_driver_call_data.new(action="answer_later", driver=driver_id))],
        [InlineKeyboardButton(text="‼️Ban",
                              callback_data=admin_driver_call_data.new(action="ban_reporter", driver=driver_id))]
    ], resize_keyboard=True)
    return keyboard


confirmation_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text=""),
        InlineKeyboardButton(text="")]
])

#
# admin_callback_data = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text="💬", )]
# ])

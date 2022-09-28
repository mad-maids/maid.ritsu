from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

give_contact_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton('📱Send my number', request_contact=True)],
        [KeyboardButton('🔙Back')]
    ], one_time_keyboard=True, resize_keyboard=True)

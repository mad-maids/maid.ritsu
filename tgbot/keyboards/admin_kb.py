from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💬Start chat', callback_data='start_chat')],
    [InlineKeyboardButton(text='🔒Ban', callback_data='start_ban'),
     InlineKeyboardButton(text='🔓Unban', callback_data='start_unban')]
])
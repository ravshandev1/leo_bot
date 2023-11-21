from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def count_btn(count: int):
    keyboard = list()
    keyboard.append([InlineKeyboardButton("-", callback_data=f'minus:{count}'),
                     InlineKeyboardButton(f'{count}', callback_data=f'{count}'),
                     InlineKeyboardButton("+", callback_data=f'plus:{count}')])
    keyboard.append([InlineKeyboardButton("Savatchaga qo'shish", callback_data=f'cart:{count}'),
                     InlineKeyboardButton("Narx", url='https://t.me/+Z36FzfUMcNRkNDQy')])
    keyboard.append([InlineKeyboardButton("⬅️Ortga", callback_data=f'back:{count}')])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

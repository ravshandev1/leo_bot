from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Brandlar"),
            KeyboardButton("Savatcham"),
        ]
    ],
    resize_keyboard=True
)
cart = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Buyurtmani berish"),
            KeyboardButton("Savatchani tozalash"),
        ],
        [
            KeyboardButton("⬅️Ortga")
        ]
    ],
    resize_keyboard=True
)

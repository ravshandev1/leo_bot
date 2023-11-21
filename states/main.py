from aiogram.dispatcher.filters.state import State, StatesGroup


class Search(StatesGroup):
    brand = State()
    category = State()
    model = State()
    product = State()
    count = State()


class Register(StatesGroup):
    name = State()
    phone = State()

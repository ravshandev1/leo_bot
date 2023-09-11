from aiogram.dispatcher.filters.state import State, StatesGroup


class Search(StatesGroup):
    name = State()


class Register(StatesGroup):
    phone = State()

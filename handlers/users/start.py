from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher.filters.builtin import CommandStart, CommandHelp
import requests
from loader import dp
from data.config import API, ADMIN
from aiogram.dispatcher import FSMContext
from states.main import Search, Register


@dp.message_handler(CommandStart())
async def bot_start(message: Message):
    r = requests.get(url=f"{API}/", params={'id': message.from_user.id})
    if r.status_code == 404:
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton("Telefon raqamni yuborish!", request_contact=True)
                ]
            ],
            resize_keyboard=True
        )
        await message.answer("Ro'yxatdan o'tish uchun telefon raqamingizni yuboring yoki yozing!", reply_markup=kb)
        await Register.phone.set()
    else:
        await message.answer("/help kamandasini bosing!")


@dp.message_handler(CommandHelp())
async def bot_help(message: Message):
    r = requests.get(url=f"{API}/", params={'id': message.from_user.id})
    if r.status_code == 200:
        rp = requests.get(url=f"{API}/brands/")
        btn = rp.json()
        keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        for i in btn:
            keyboard.insert(
                KeyboardButton(text=f"{i['name']}")
            )
        await message.answer('Brandni tanlang!', reply_markup=keyboard)
    else:
        await message.answer('Tasdiqlanmagan foydalanuvchi!')


@dp.message_handler(state=Register.phone, content_types=['contact', 'text'])
async def register(ms: Message, state: FSMContext):
    if ms.contact:
        phone = ms.contact.phone_number
    else:
        phone = ms.text
    requests.post(url=f"{API}/", data={'tele_id': ms.from_user.id, 'username': ms.from_user.username,
                                       'first_name': ms.from_user.first_name, 'last_name': ms.from_user.last_name,
                                       'phone': phone})
    await dp.bot.send_message(ADMIN,
                              f"Yangi foydalanuvchi\nAdmin panelga kirib {phone} raqamdagi foydalanuvchini tasdiqlang!")
    await ms.answer(
        f"Salom, {ms.from_user.full_name}!\nRo'yxatdan o'tdingiz. Admin ruxsat bersa botdan foydalanishingiz mumkin!",
        reply_markup=ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(state=Search.name)
async def search_func(mes: Message, state: FSMContext):
    if mes.text == '⬅️Ortga':
        r = requests.get(url=f"{API}/", params={'id': mes.from_user.id})
        if r.status_code == 200:
            rp = requests.get(url=f"{API}/brands/")
            btn = rp.json()
            keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            for i in btn:
                keyboard.insert(
                    KeyboardButton(text=f"{i['name']}")
                )
            await mes.answer('Brandni tanlang!', reply_markup=keyboard)
        else:
            await mes.answer('Tasdiqlanmagan foydalanuvchi!')
        await state.finish()
    else:
        br = await state.get_data()
        rq = requests.get(url=f"{API}/products/", params={'br': br['brand'], 'name': mes.text})
        if rq.status_code == 200:
            dt = rq.json()
            txt = ""
            txt += dt['name']
            if dt['description']:
                txt.join(dt['description'])
            else:
                txt.join('')
            for i in dt['images']:
                await mes.answer_photo(photo=open(f"{i['image_path']}", 'rb'))
            await mes.answer(txt)
        else:
            await mes.answer("Bunday mahsulot topilmadi!!!")


@dp.message_handler(state=None)
async def main_func(mes: Message, state: FSMContext):
    r = requests.get(url=f"{API}/", params={'id': mes.from_user.id})
    if r.status_code == 200:
        rp = requests.get(url=f"{API}/brands/")
        btn = rp.json()
        ls = [i['name'] for i in btn]
        if mes.text in ls:
            await state.set_data(
                {'brand': mes.text}
            )
            kb = ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton('⬅️Ortga')
                    ]
                ],
                resize_keyboard=True
            )
            await Search.name.set()
            await mes.answer(f"<b>{mes.text}</b> brendi buyicha mahsulot nomini kiriting!", reply_markup=kb)
        else:
            await mes.answer("Brandlarni ko'rish uchun /help komandasini bosing!")
    else:
        await mes.answer('Tasdiqlanmagan foydalanuvchi!')

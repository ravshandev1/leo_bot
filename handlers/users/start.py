from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, CallbackQuery
import requests
from loader import dp
from data.config import API, ADMIN
from aiogram.dispatcher import FSMContext
from states.main import Search, Register
from keyboards.inline.main import count_btn
from keyboards.default.main import main_btn, cart


@dp.message_handler(commands=['start'])
async def bot_start(message: Message):
    r = requests.get(url=f"{API}/", params={'id': message.from_user.id})
    if r.status_code == 404:
        await message.answer("Ro'yxatdan o'tish uchun ismingizni yozing!")
        await Register.name.set()
    elif r.status_code == 200:
        await message.answer("Bo'limni tanlang!", reply_markup=main_btn)
    else:
        await message.answer("Tasdiqlanmagan foydalanuvchi!")


@dp.message_handler(text=['Brandlar'])
async def bot_help(mes: Message):
    r = requests.get(url=f"{API}/", params={'id': mes.from_user.id})
    if r.status_code == 200:
        rp = requests.get(url=f"{API}/brands/")
        btn = rp.json()
        keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        for i in btn:
            keyboard.insert(KeyboardButton(text=f"{i['name']}"))
        keyboard.insert(KeyboardButton("⬅️Ortga"))
        await Search.brand.set()
        await mes.answer('Brandni tanlang!', reply_markup=keyboard)
    else:
        await mes.answer('Tasdiqlanmagan foydalanuvchi!')


@dp.message_handler(text=['Savatcham'])
async def a(mes: Message):
    r = requests.get(url=f"{API}/my-cart/{mes.from_user.id}/")
    dt = r.json()
    txt = ""
    for i in dt['results']:
        txt += f"<b>{i['product']}</b> dan <b>{i['count']}</b> ta - <b>{i['total_price']}</b> so'm\n"
    txt += f"\nJami: <b>{dt['total_price']}</b> so'm"
    await mes.answer(txt, reply_markup=cart)


@dp.message_handler(text=['Buyurtmani berish', 'Savatchani tozalash', '⬅️Ortga'])
async def a(mes: Message):
    if mes.text == '⬅️Ortga':
        await mes.answer("Bo'limni tanlang!", reply_markup=main_btn)
    elif mes.text == 'Buyurtmani berish':
        r = requests.put(url=f"{API}/my-cart/{mes.from_user.id}/")
        if r.status_code == 200:
            await mes.answer("Buyurtma muvafiqiyatli junatildi!\nBo'limni tanlang!", reply_markup=main_btn)
        else:
            await mes.answer("Xato\nQaytadan urinib kuring!")
    elif mes.text == 'Savatchani tozalash':
        requests.delete(url=f"{API}/my-cart/{mes.from_user.id}/")
        await mes.answer("Savatchangiz tozalandi!\nBo'limni tanlang!", reply_markup=main_btn)


@dp.message_handler(state=Register.name)
async def a(mes: Message, state: FSMContext):
    await state.update_data({'first_name': mes.text})
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton("Telefon raqamni yuborish!", request_contact=True)
            ]
        ],
        resize_keyboard=True
    )
    await mes.answer("Telefon raqamingizni yuboring yoki yozing!", reply_markup=kb)
    await Register.next()


@dp.message_handler(state=Register.phone, content_types=['contact', 'text'])
async def register(ms: Message, state: FSMContext):
    data = await state.get_data()
    if ms.contact:
        phone = ms.contact.phone_number
    else:
        phone = ms.text
    requests.post(url=f"{API}/", data={'tele_id': ms.from_user.id, 'username': ms.from_user.username, 'phone': phone,
                                       'first_name': data['first_name'], 'last_name': ms.from_user.last_name})
    await dp.bot.send_message(ADMIN,
                              f"Yangi foydalanuvchi\nAdmin panelga kirib {phone} raqamdagi foydalanuvchini tasdiqlang!")
    await ms.answer(
        f"Assalomu alaykum, {data['first_name']}!\nRo'yxatdan o'tdingiz. Admin ruxsat bersa botdan foydalanishingiz mumkin!",
        reply_markup=ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(state=Search.brand)
async def search_func(mes: Message, state: FSMContext):
    if mes.text == '⬅️Ortga':
        await mes.answer("Bo'limni tanlang!", reply_markup=main_btn)
        await state.finish()
    else:
        r = requests.get(url=f"{API}/categories/", params={'brand': mes.text})
        btn = r.json()
        keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        for i in btn:
            keyboard.insert(KeyboardButton(f"{i['name']}"))
        keyboard.insert(KeyboardButton("⬅️Ortga"))
        await mes.answer("Categoriyani tanlang!", reply_markup=keyboard)
        await Search.next()
        await state.update_data({'brand': mes.text})


@dp.message_handler(state=Search.category)
async def a(mes: Message, state: FSMContext):
    data = await state.get_data()
    if mes.text == "⬅️Ortga":
        r = requests.get(url=f"{API}/brands/")
        btn = r.json()
        keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        for i in btn:
            keyboard.insert(KeyboardButton(f"{i['name']}"))
        keyboard.insert(KeyboardButton("⬅️Ortga"))
        await mes.answer("Brandni tanlang!", reply_markup=keyboard)
        await Search.previous()
    else:
        r = requests.get(url=f"{API}/categories/", params={'brand': data['brand']})
        btn = r.json()
        ls = [i['name'] for i in btn]
        if mes.text in ls:
            r = requests.get(url=f"{API}/models/", params={'brand': data['brand'], 'category': mes.text})
            btn = r.json()
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            for i in btn:
                keyboard.insert(KeyboardButton(f"{i['name']}"))
            keyboard.insert(KeyboardButton("⬅️Ortga"))
            await mes.answer("Modelni tanlang!", reply_markup=keyboard)
            await state.update_data({'category': mes.text})
            await Search.next()
        else:
            r = requests.get(url=f"{API}/images/", params={'product': mes.text})
            r2 = requests.get(url=f"{API}/product-detail/", params={'product': mes.text})
            dt = r.json()
            dt2 = r2.json()
            if dt:
                for i in dt:
                    image = requests.get(url=i['image_path'])
                    await mes.answer_photo(photo=image.content, reply_markup=ReplyKeyboardRemove())
                await mes.answer(f"{dt2['description']}\nNarxi: {dt2['price']}$", reply_markup=count_btn(1))
                await Search.next()
                await state.update_data({'product': mes.text})
            else:
                await mes.answer("Bunday product topilmadi!")


@dp.message_handler(state=Search.model)
async def a(mes: Message, state: FSMContext):
    data = await state.get_data()
    if mes.text == "⬅️Ortga":
        r = requests.get(url=f"{API}/categories/", params={'brand': data['brand']})
        btn = r.json()
        keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        for i in btn:
            keyboard.insert(KeyboardButton(f"{i['name']}"))
        keyboard.insert(KeyboardButton("⬅️Ortga"))
        await mes.answer("Categoriyani tanlang!", reply_markup=keyboard)
        await Search.previous()
    else:
        r = requests.get(url=f"{API}/products/",
                         params={'brand': data['brand'], 'category': data['category'], 'model': mes.text})
        btn = r.json()
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for i in btn:
            keyboard.insert(KeyboardButton(f"{i['name']}"))
        keyboard.insert(KeyboardButton("⬅️Ortga"))
        await mes.answer("Productni tanlang!", reply_markup=keyboard)
        await state.update_data({'model': mes.text})
        await Search.next()


@dp.message_handler(state=Search.product)
async def a(mes: Message, state: FSMContext):
    data = await state.get_data()
    if mes.text == "⬅️Ortga":
        r = requests.get(url=f"{API}/models/", params={'brand': data['brand'], 'category': data['category']})
        btn = r.json()
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for i in btn:
            keyboard.insert(KeyboardButton(f"{i['name']}"))
        keyboard.insert(KeyboardButton("⬅️Ortga"))
        await mes.answer("Modelni tanlang!", reply_markup=keyboard)
        await Search.previous()
    else:
        r = requests.get(url=f"{API}/images/", params={'product': mes.text})
        r2 = requests.get(url=f"{API}/product-detail/", params={'product': mes.text})
        dt = r.json()
        dt2 = r2.json()
        if dt:
            for i in dt:
                image = requests.get(url=i['image_path'])
                await mes.answer_photo(photo=image.content, reply_markup=ReplyKeyboardRemove())
            if dt2['description']:
                await mes.answer(f"{dt2['description']}\nNarxi: {dt2['price']}$", reply_markup=count_btn(1))
            else:
                await mes.answer(f"Narxi: {dt2['price']}$", reply_markup=count_btn(1))
            await Search.next()
            await state.update_data({'product': mes.text})
        else:
            await mes.answer("Bunday product topilmadi!")


@dp.callback_query_handler(state=Search.count)
async def a(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    count = int(call.data.split(':')[1])
    action = call.data.split(':')[0]
    if action == "plus":
        r = requests.get(url=f"{API}/product-detail/", params={'product': data['product']})
        dt = r.json()
        if dt['description']:
            await call.message.edit_text(f"{dt['description']}\nNarxi: {dt['price']}$", reply_markup=count_btn(count + 1))
        else:
            await call.message.edit_text(f"Narxi: {dt['price']}$", reply_markup=count_btn(count + 1))
    elif action == 'minus' and count > 1:
        r = requests.get(url=f"{API}/product-detail/", params={'product': data['product']})
        dt = r.json()
        if dt['description']:
            await call.message.edit_text(f"{dt['description']}\nNarxi: {dt['price']}$",
                                         reply_markup=count_btn(count - 1))
        else:
            await call.message.edit_text(f"Narxi: {dt['price']}$", reply_markup=count_btn(count - 1))
    elif action == 'cart':
        requests.post(url=f"{API}/my-cart/{call.from_user.id}/", data={'product': data['product'], 'count': count})
        await call.message.answer("Savatchaga qo'shildi!\nBo'limni tanlang!", reply_markup=main_btn)
        await state.finish()
    elif action == 'back':
        await call.message.delete()
        r = requests.get(url=f"{API}/products/",
                         params={'brand': data['brand'], 'category': data['category'], 'model': data['model']})
        btn = r.json()
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for i in btn:
            keyboard.insert(KeyboardButton(f"{i['name']}"))
        keyboard.insert(KeyboardButton("⬅️Ortga"))
        await call.message.answer("Productni tanlang!", reply_markup=keyboard)
        await Search.model.set()
    await call.answer(cache_time=2)


@dp.message_handler(state=None)
async def main_func(mes: Message):
    r = requests.get(url=f"{API}/", params={'id': mes.from_user.id})
    if r.status_code == 200:
        await mes.answer("Bo'limni tanlang!", reply_markup=main_btn)
    else:
        await mes.answer('Tasdiqlanmagan foydalanuvchi!')

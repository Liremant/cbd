import asyncio
import os
from aiogram import F, Bot, Dispatcher, Router
from aiogram.types import Message, CallbackQuery   
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from app.database.models import async_main
import app.keyboards as kb
import app.database.requests as rq
from crystalpayio import CrystalPayIO 
from aiogram.methods.send_message import SendMessage
load_dotenv()
global bot
bot = Bot(token=os.getenv('TOKEN'))
router = Router()
admin_router = Router()  # Новый роутер для админ-команд
crystal = CrystalPayIO(os.getenv("AUTH_LOGIN"),os.getenv("AUTH_SECRET"))


class Register(StatesGroup):
    name = State()
    age = State()
    number = State()

class CartState(StatesGroup):
    item_id = State()
    quantity = State()

class AdminState(StatesGroup):
    category_name = State()
    edit_category_name = State()
    new_item_name = State()
    new_item_image = State()
    new_item_description = State()
    new_item_price = State()
    edit_item_details = State()
    sale_name = State()
    sale_desc = State()
    sale_price = State()
    promo_writing = State()
    pay_guess = State()


ADMIN_ID =os.getenv('ADMIN_IDS')

def is_admin(user_id):
    return str(user_id) in str(ADMIN_ID)
@router.message(F.text == 'О нас')
async def about_us(message : Message):
    await message.answer('Да хуй знает наркотики делаем')

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет!Пройди простую авторизацию в боте,чтобы мы открыли тебе доступ', reply_markup=kb.auth)
    await message.delete()
@router.message(F.contact)
async def main(message: Message):
    await rq.set_user(tg_id=message.from_user.id,number=message.contact.phone_number)
    await message.answer('Тебя приветствует CBD Mana Organic shop!Здесь вы можете найти наркотики и маму агнии',reply_markup=kb.main)
    await message.answer('')
    await message.delete()
@router.message(F.text == 'Каталог')
async def catalog(message: Message):
    await message.answer('Выберите категорию товара', reply_markup=await kb.categories())
    await message.delete()
@router.callback_query(F.data == 'to_main')
async def go_main(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('Тебя приветствует CBD Mana Organic shop!Здесь вы можете найти наркотики и маму агнии',reply_markup=kb.main)
@router.message(F.text =='Контакты')
async def contacts(message : Message):
    await message.delete()
    await message.answer(f'Контактный номер:+7 (987) 269-08-66\nНаш канал: t.me/CBDima\n Мы на Яндекс маркете:<a href="https://market.yandex.ru/business--cbdima/122026290">*нажать*</a>',reply_markup=kb.contacts(),parse_mode='HTML',disable_web_page_preview=True)

@router.message(F.text == 'Корзина')
async def show_cart(message: Message):
    cart_items = await rq.get_cart(message.from_user.id)
    await message.delete()
    if not cart_items:
        await message.answer('Ваша корзина пуста.', reply_markup=kb.main)
    else:
        total_sum = sum(item['item'].price * item['quantity'] for item in cart_items)
        items_keyboard = await kb.cart_items(cart_items, total_sum)
        await message.answer(f'Содержимое вашей корзины:', reply_markup=items_keyboard)
        
@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('Выберите ТОВАРЧИК', reply_markup=await kb.items(callback.data.split('_')[1]))
    await callback.message.delete()
@router.callback_query(F.data.startswith('item_'))
async def item(callback: CallbackQuery):
    item_data = await rq.get_item(callback.data.split('_')[1])
    img_id = item_data.img_id
    await callback.message.delete()
    await callback.answer() 
    await callback.message.answer_photo(photo=await rq.get_image(img_id),
                                        caption=f'Название: {item_data.name}\ndesc:{item_data.description}\nPrice: {item_data.price} рублекофф',
                                        reply_markup=await kb.item_options(callback.data.split('_')[1]))

@router.callback_query(F.data.startswith('to_cart_'))
async def ask_quantity(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    try:
        item_id = int(callback.data.split('_')[2])
        await state.update_data(item_id=item_id)
        await state.set_state(CartState.quantity)
        await callback.message.answer('Введите количество товара:')
    except:
        callback.message('Число слишком большое!')


@router.message(CartState.quantity)
async def add_to_cart(message: Message, state: FSMContext):
    await message.delete()

    if not message.text.isdigit():
        await message.answer('Пожалуйста, введите число.')
        return
    
    quantity = int(message.text)
    user_data = await state.get_data()
    item_id = user_data.get('item_id')

    await rq.add_to_cart(message.from_user.id, item_id, quantity)
    await state.clear()
    await message.answer('Товар добавлен в корзину!', reply_markup=kb.main)

@router.callback_query(F.data == 'clear_cart')
async def clear_cart(callback: CallbackQuery):
    await callback.message.delete()
    await rq.clear_cart(callback.from_user.id)
    await callback.answer('Корзина очищена!')
    await callback.message.answer('Ваша корзина пуста.', reply_markup=kb.main)
    await callback.message.delete()


async def create_invoice() -> tuple:
    invoice = await crystal.invoice.create(
        total_sum, # Цена
        30, # Время жизни чека (в минутах)
        amount_currency="RUB" # Валюта
    )
    print('create invoice with id:',invoice.id)
    return(invoice.url,invoice.id)


async def invoice_handler(id: str, message: Message) -> None:
    while True:
        invoice = await crystal.invoice.get(id)
        if invoice.state == "payed":
            await message.answer("Счёт успешно оплачен!")
            await rq.clear_cart(message.from_user.id)
            cart_items = await rq.get_cart(message.from_user.id)    
            try:
                await bot.send_message(chat_id=os.getenv("ADMIN_IDS"),text=f'Поступил заказ от:@{message.from_user.username} (username) / {message.from_user.id} (id),с промокодом:{user_promo},в заказе:')
                for cart_item in cart_items:
                    item = cart_item['item']
                    quantity = cart_item['quantity']
                    for i in os.getenv("ADMIN_IDS"):
                        print(i)
                        await bot.send_message(chat_id=i,text=(f'{item.name} ({quantity} шт.) - {item.price} руб.'))                          
            except:
                await bot.send_message(chat_id=os.getenv("ADMIN_IDS"),text=f'Поступил заказ от:@{message.from_user.username} (username) / {message.from_user.id} (id),в заказе:{await rq.get_cart(message.from_user.id)}')
                for cart_item in cart_items:
                    item = cart_item['item']
                    quantity = cart_item['quantity']
                    for i in os.getenv("ADMIN_IDS"):
                        print(f'chat_id{i}')
                        await bot.send_message(chat_id=i,text=(f'{item.name} ({quantity} шт.) - {item.price} руб.'))  
            break
        await asyncio.sleep(15) # Задержка



@router.callback_query(F.data == "pay_cart")
async def buy_handler(callback: CallbackQuery, state : FSMContext) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    print(user_id)
    cart_items = await rq.get_cart(user_id)
    await callback.message.delete()
    if not cart_items:
        await callback.message.answer('Ваша корзина пуста. Добавьте товары, чтобы продолжить покупку.')
        return
    else:
        global total_sum
        total_sum = sum(item['item'].price * item['quantity'] for item in cart_items)
        await callback.message.answer(text=f'У вас есть промокод?,Если да,то введите его в чат',reply_markup=kb.promo())
        await state.set_state(AdminState.promo_writing)
@router.message(AdminState.promo_writing, F.text)
async def promo_checker(message : Message, state : FSMContext):
    all_sales = await rq.get_sales()
    global user_promo
    user_promo = message.text.lower()
    
    for sale in all_sales:
        if user_promo == sale.name.lower():
            await rq.get_sale(sale.id)
            await message.answer('Промокод был успешно приминен!')
            global total_sum
            total_sum = total_sum - int(sale.price)
            await message.answer(f'Сумма корзины: {total_sum} рублей \n Выберите способ оплаты:', reply_markup=kb.pay_options())
            await state.clear()
            break
    else:
        await message.answer('Такого промокода не существует!') 
    


@router.callback_query(F.data == 'pay_crypto')
async def buy_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    invoice_task = asyncio.create_task(create_invoice())
    invoice_result = await invoice_task
    invoice_pay= invoice_result[0]
    await callback.message.answer(text=f"Сумма заказа:{total_sum} рублей.\nПерейдите по ссылке:",reply_markup=kb.pay_crypto1(invoice_pay))
    await callback.answer()

    asyncio.create_task(invoice_handler(invoice_result[1], callback.message))
# Админские команды
@admin_router.message(Command('admin'))
async def admin_panel(message: Message):
    await message.delete()
    if is_admin(message.from_user.id):
        await message.answer('Вы вошли в админ панель! Выберите действие:',
                             reply_markup=kb.admin_main())
    else:
        await message.answer('У вас нет доступа к этой команде.')

@admin_router.callback_query(F.data == 'edit_categories')
async def edit_categories(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer('Выберите категорию:', reply_markup=await kb.admin_categories())

@admin_router.callback_query(F.data == 'add_category')
async def add_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введите название новой категории:')
    await state.set_state(AdminState.category_name)

@admin_router.message(AdminState.category_name)
async def save_new_category(message: Message, state: FSMContext):
    await message.delete()
    category_name = message.text
    await rq.add_category(category_name)
    await state.clear()
    await message.answer('Категория добавлена!', reply_markup=await kb.admin_categories())

@admin_router.callback_query(F.data.startswith('edit_category_'))
async def edit_category(callback: CallbackQuery):
    await callback.answer()
    category_id = int(callback.data.split('_')[2])
    await callback.message.answer(f'Выберите действие',
                                  reply_markup=kb.edit_category_options(category_id))

@admin_router.callback_query(F.data.startswith('delete_category_'))
async def delete_category(callback: CallbackQuery):
    await callback.answer()
    category_id = int(callback.data.split('_')[2])
    await rq.delete_category(category_id)
    await callback.message.answer('Категория удалена!', reply_markup=await kb.admin_categories())

@admin_router.callback_query(F.data.startswith('rename_category_'))
async def rename_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    category_id = int(callback.data.split('_')[2])
    await state.update_data(category_id=category_id)
    await callback.message.answer('Введите новое название категории:')
    await state.set_state(AdminState.edit_category_name)

@admin_router.message(AdminState.edit_category_name)
async def save_new_category_name(message: Message, state: FSMContext):
    await message.delete()
    new_name = message.text
    user_data = await state.get_data()
    category_id = user_data.get('category_id')
    await rq.rename_category(category_id, new_name)
    await state.clear()
    await message.answer('Название категории обновлено!', reply_markup=await kb.admin_categories())

@admin_router.callback_query(F.data == 'edit_items')
async def edit_items(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.answer('')
    await callback.message.answer('Выберите категорию:', reply_markup=await kb.admin_categoriess())

@admin_router.callback_query(F.data.startswith('edit_items_'))
async def select_item_category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    category_id = int(callback.data.split('_')[2])
    items = await rq.get_category_item(category_id)
    global it1m
    it1m = items
    if items == None:
        await callback.message.answer('В этой категории пока нет товаров. Вы можете добавить новый товар.', reply_markup=await kb.admin_items(category_id, empty=True))
    else:
        await callback.message.answer('Выберите товар:', reply_markup=await kb.admin_items(category_id))

@admin_router.callback_query(F.data.startswith('edit_item_'))
async def edit_item(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    item_id = int(callback.data.split('_')[2])
    item = await rq.get_item(item_id)
    category_id = int(callback.data.split('_')[2])
    print(item.img_id)
    await callback.message.reply_photo(photo=await rq.get_image(item.img_id),
                                        caption=f'Название: {item.name}\nОписание: {item.description}\nЦена: {item.price} руб.',
                                        reply_markup=kb.edit_item_options(item_id,category_id))

@admin_router.callback_query(F.data == 'edit_sales')
async def edit_items(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer('')
    await callback.message.answer('Выберите акцию:', reply_markup=await kb.admin_sales())
@admin_router.callback_query(F.data == 'add_sale')
async def rename_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer('Введите название промокода/акции:')
    await state.set_state(AdminState.sale_name)

@admin_router.callback_query(F.data.startswith('edit_sale_'))
async def edit_item(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    sale_id = int(callback.data.split('_')[2])
    sale = await rq.get_sale(sale_id)
    
    
    if sale.price == 0:
        await callback.message.answer(text=f'Название:{sale.name}\n \n.{sale.description}',reply_markup=kb.edit_sale_options(sale_id))
    
    else:
        await callback.message.answer(
                                        text=f'Название: {sale.name}\n{sale.description}\nскидка: {sale.price}р',
                                        reply_markup=kb.edit_sale_options(sale_id))

@admin_router.callback_query(F.data.startswith('rename_sale_'))
async def rename_sale(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    sale_id = int(callback.data.split('_')[2])
    await rq.delete_sale(sale_id)
    await state.update_data(sale_id=sale_id)
    await callback.message.answer('Введите название промокода/акции:')
    await state.set_state(AdminState.sale_name)

@admin_router.message(AdminState.sale_name)
async def save_new_sale(message: Message, state: FSMContext):
    sale_name = message.text
    await message.delete()
    await message.answer('Введите,сколько бонусов будет давать акция(если суть акции не в этом - впишите 0)')
    await state.update_data(sale_name=sale_name)
    await state.set_state(AdminState.sale_price)

@admin_router.message(AdminState.sale_price)
async def sale_price(message : Message, state: FSMContext):
    sale_price = int(message.text)
    await message.delete()
    await state.update_data(sale_price=sale_price)
    await state.set_state(AdminState.sale_desc)
    await message.answer('Введите описание акции')
@admin_router.message(AdminState.sale_desc)    
async def sale_desc(message : Message, state: FSMContext):
    description = message.text
    user_data = await state.get_data()
    sale_name = user_data.get('sale_name')
    sale_price = user_data.get('sale_price')

    message.delete()
    await rq.add_sale(sale_name, sale_price, description)
    await state.clear()
    await message.answer('Новая акция добавлена!', reply_markup=await kb.admin_sales())

@admin_router.callback_query(F.data.startswith('delete_sale_'))
async def delete_item(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    sale_id = int(callback.data.split('_')[2])
    await rq.delete_sale(sale_id)
    await callback.message.answer('Товар удален!', reply_markup=await kb.admin_sales())

@admin_router.callback_query(F.data.startswith('delete_item_'))
async def delete_item(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    item_id = int(callback.data.split('_')[2])
    await rq.delete_item(item_id)
    await callback.message.answer('Товар удален!', reply_markup=await kb.admin_categories())

@admin_router.callback_query(F.data.startswith('cont_'))
async def delete_item(callback: CallbackQuery):
    await callback.message.delete()
    item_id = int(callback.data.split('_')[2])
    await rq.delete_item(item_id)
    await callback.message.answer('Нажмите продолжить,чтобы ввести новые параметры товара', reply_markup=await kb.cont())

@admin_router.callback_query(F.data.startswith('new_item_'))
async def add_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    category_id = int(callback.data.split('_')[2])
    await state.update_data(category_id=category_id)
    await callback.message.answer('Введите название нового товара:')
    await state.set_state(AdminState.new_item_name)

@admin_router.message(AdminState.new_item_name)
async def new_item_name(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(new_item_name=message.text)
    await state.set_state(AdminState.new_item_image)
    await message.answer('Отправьте изображение нового товара:')
    print('send_photo 1')
   
   

@admin_router.message(AdminState.new_item_image, F.photo)
async def download_photo(message: Message, state : FSMContext):
    global img_id
    img_id = message.photo[-1].file_id
    print(img_id)
    await state.update_data(new_item_image=img_id)
    await state.set_state(AdminState.new_item_description)
    await message.answer('Введите описание нового товара:')
    await message.delete(message.chat_id,int(message.id)-1)
@admin_router.message(AdminState.new_item_description)
async def new_item_description(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(new_item_description=message.text)
    await state.set_state(AdminState.new_item_price)
    await message.answer('Введите цену нового товара:')

@admin_router.message(AdminState.new_item_price)
async def new_item_price(message: Message, state: FSMContext):
    await message.delete()
    if not message.text.isdigit():
        await message.answer('Пожалуйста, введите число.')
        return
    
    price = int(message.text)
    user_data = await state.get_data()
    category_id = user_data.get('category_id')
    name = user_data.get('new_item_name')
    description = user_data.get('new_item_description')
    await rq.add_item(name, price, description, img_id, category_id)
    await state.clear()
    await message.answer('Товар добавлен успешно!', reply_markup=await kb.admin_items(category_id))

async def main():
    await async_main()

    dp = Dispatcher()
    await dp.start_polling(bot)


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from app.database.requests import get_categories, get_category_item, get_sales
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

#auth=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Поделиться номером телефона☎')]]request_contact=True,resize_keyboard=True,input_field_placeholder='Пройдите авторизацию...')

auth = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Поделиться номером телефона☎', request_contact=True)
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Пройдите авторизацию...'
)



main=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Каталог')],
                                     [KeyboardButton(text='Корзина')],
                                     [KeyboardButton(text='Контакты'), KeyboardButton(text='О нас')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')

def contacts():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Маркет',url='https://market.yandex.ru/business--cbdima/122026290'))
    keyboard.add(InlineKeyboardButton(text='Канал',url='https://t.me/CBDima'))
    return keyboard.adjust(2).as_markup()
async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'category_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()

async def items(category_id):
    all_items = await get_category_item(category_id)
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f'item_{item.id}'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()
def promo():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Нет',callback_data=f'pay_crypto'))
    return keyboard.as_markup()
async def item_options(item_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='В корзину', callback_data=f'to_cart_{item_id}'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.as_markup()

async def cart_items(cart_items, total_sum):
    keyboard = InlineKeyboardBuilder()
    for cart_item in cart_items:
        item = cart_item['item']
        quantity = cart_item['quantity']
        keyboard.add(InlineKeyboardButton(text=f'{item.name} ({quantity} шт.) - {item.price} руб.', callback_data=f'item_{item.id}'))
    keyboard.add(InlineKeyboardButton(text='Оплатить корзину', callback_data='pay_cart'))
    keyboard.add(InlineKeyboardButton(text='Очистить корзину', callback_data='clear_cart'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    keyboard.adjust(3)
    return keyboard.as_markup()

def pay_options():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Оплатить по карте', callback_data='pay_yoomoney'))
    keyboard.add(InlineKeyboardButton(text='Оплатить криптовалютой', callback_data='pay_crypto'))
    return keyboard.as_markup()

def admin_main():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Редактировать категории', callback_data='edit_categories'))
    keyboard.add(InlineKeyboardButton(text='Редактировать товары', callback_data='edit_items'))
    keyboard.add(InlineKeyboardButton(text='Редактировать акции',callback_data='edit_sales'))
    return keyboard.adjust(2).as_markup()

async def admin_categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'edit_category_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='Добавить категорию', callback_data='add_category'))
    return keyboard.adjust(2).as_markup()

async def admin_sales():
    all_sales = await get_sales()
    keyboard = InlineKeyboardBuilder()
    for sale in all_sales:
        keyboard.add(InlineKeyboardButton(text=sale.name,callback_data=f'edit_sale_{sale.id}'))
    keyboard.add(InlineKeyboardButton(text='Добавить акцию',callback_data='add_sale'))
    return keyboard.adjust(2).as_markup()

def edit_sale_options(sale_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Удалить акцию',callback_data=f'delete_sale_{sale_id}'))
    keyboard.add(InlineKeyboardButton(text='Редактировать акцию',callback_data=f'rename_sale_{sale_id}'))
    return keyboard.as_markup()
async def admin_categoriess():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'edit_items_{category.id}'))
    return keyboard.adjust(2).as_markup()

def edit_category_options(category_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Удалить категорию', callback_data=f'delete_category_{category_id}'))
    keyboard.add(InlineKeyboardButton(text='Редактировать категорию', callback_data=f'rename_category_{category_id}'))
    return keyboard.as_markup()

async def admin_items(category_id):
    all_items = await get_category_item(category_id)
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Добавить товар', callback_data=f'new_item_{category_id}'))
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f'edit_item_{item.id}'))
    keyboard.add(InlineKeyboardButton(text='Вернуться в меню', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()
def pay_crypto1(invoice_result):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Перейти', url = f'{invoice_result}'))
    return keyboard.as_markup()
def cont(category_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Продолжить',callback_data=f'new_item_{category_id}'))
    return keyboard.as_markup()

def edit_item_options(item_id,category_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Удалить товар', callback_data=f'delete_item_{item_id}'))
    keyboard.add(InlineKeyboardButton(text='Редактировать товар', callback_data=f'сont_{category_id}'))
    return keyboard.as_markup()

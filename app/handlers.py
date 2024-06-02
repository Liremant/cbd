from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as rq
router = Router()


class Register(StatesGroup):
    name = State()
    age = State()
    number = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer('Привет!', reply_markup=kb.main)


@router.message(F.text == 'Каталог')
async def catalog(message : Message):
    await message.answer('Выберите категорию товара',reply_markup=await kb.categories())


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('ИДИ НАХУЙ КАТЕГОРИЮ ВЫБРАЛ')
    await callback.message.answer('Выберите литры спермы',
                                  reply_markup=await kb.items(callback.data.split('_')[1]))
    



@router.callback_query(F.data.startswith('item_'))
async def category(callback: CallbackQuery):
    item_data = await rq.get_item(callback.data.split('_')[1])
    await callback.answer('ИДИ НАХУЙ ТОВАР ВЫБРАЛ')
    await callback.message.answer(f'Название:{item_data.name}\nDesc:{item_data.description}\nprice:{item_data.price} рублекофф ',
                                  reply_markup=await kb.items(callback.data.split('_')[1]))


#@router.callback_query(F.data == 'add_to_cart')
#async def add_cart(callback : CallbackQuery):
#    item_data = await rq.get_item(callback.data.split('_')[1])
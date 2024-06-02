import asyncio
from aiogram import Bot, Dispatcher

from app.handlers import router
from app.database.models import async_main

import logging

logging.basicConfig(level=logging.INFO)

async def main():
    await async_main()
    bot = Bot(token='7017434654:AAFhiiquftwR_ixbYAnj2EPyaCrnhnUugiw')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')

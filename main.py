import asyncio, logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import config
from db import init_db, AsyncSessionLocal
from handlers import start, shop, balance, history, admin, common

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Init DB
    await init_db()

    bot = Bot(token=config.TOKEN, parse_mode='HTML')
    dp = Dispatcher(storage=MemoryStorage())

    # register routers (each handler module defines 'router')
    dp.include_router(start.router)
    dp.include_router(shop.router)
    dp.include_router(balance.router)
    dp.include_router(history.router)
    dp.include_router(admin.router)
    dp.include_router(common.router)

    logger.info('Bot started')
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())

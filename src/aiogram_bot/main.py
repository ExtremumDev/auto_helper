import asyncio

from src.aiogram_bot.bot import dp, bot
from src.aiogram_bot.handlers import register_all_handlers


async def on_shutdown():
    pass


async def main():
    register_all_handlers(dp)

    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

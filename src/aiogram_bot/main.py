import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.aiogram_bot.bot import dp, bot
from src.aiogram_bot.handlers import register_all_handlers
from src.aiogram_bot.services.context import ServiceContext


async def on_shutdown():
    pass


async def main():
    ServiceContext.create_defaults()
    register_all_handlers(dp)

    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

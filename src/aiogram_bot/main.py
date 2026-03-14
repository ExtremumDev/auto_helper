import asyncio
import sys
from pathlib import Path


sys.path.append(str(Path(__file__).parent.parent.parent))

from src.aiogram_bot.services.app_messaging import PyrogramAppProcedureCall
from src.aiogram_bot.services.data.tg_auth import TelegramAuthManager
from src.aiogram_bot.services.data.user import UserService

from src.aiogram_bot.bot import dp, bot

from src.aiogram_bot.handlers import register_all_handlers
from src.aiogram_bot.logger import setup_logger


async def on_shutdown():
    pass


def create_service_instances():
    UserService.create_instance()
    PyrogramAppProcedureCall.create_instance()
    TelegramAuthManager.create_instance()


async def main():
    setup_logger()
    create_service_instances()

    asyncio.create_task(PyrogramAppProcedureCall().get_instance().response_loop())
    register_all_handlers(dp)

    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

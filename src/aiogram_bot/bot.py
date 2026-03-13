import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.aiogram_bot.config import settings

PROXY_URL = "http://138.36.138.218:8000"

PROXY_AUTH = aiohttp.BasicAuth(login="CT9Tjb", password="oHFCD2")

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

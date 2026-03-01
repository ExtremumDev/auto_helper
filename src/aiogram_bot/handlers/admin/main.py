from aiogram import types, Dispatcher
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

from src.aiogram_bot.filters.user import AdminFilter


async def on_start_cmd(m: types.Message, state: FSMContext, *args, **kwargs):
    pass



def register_main_admin_handlers(dp: Dispatcher):
    dp.message.register(on_start_cmd, CommandStart(), AdminFilter(), StateFilter('*'))

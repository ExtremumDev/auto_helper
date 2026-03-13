from pyrogram import Client
from pyrogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database.core.database import connection
from src.common.database.dao.user import TelegramAccountDAO
from src.pyrogram.services.orders_filtering.orders_filter import is_order_suitable_for_user


@connection
async def handle_post_in_group(client: Client, message: Message, db_session: AsyncSession, *args):
    tg_account = await TelegramAccountDAO.get_account_with_user(
        db_session=db_session,
        telegram_id=client.me.id
    )

    if tg_account:
        if message.text:
            if is_order_suitable_for_user(tg_account.user, message.text):


import asyncio
import os
import json
import pickle
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from pyrogram import Client
from pyrogram.errors import (
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid,
    FloodWait,
    ApiIdInvalid,
    AuthKeyInvalid,
    SessionRevoked,
    UserDeactivated,
    UserDeactivatedBan, AuthKeyUnregistered, PhoneNumberFlood, PhoneNumberBanned, PhoneNumberOccupied,
    PhoneCodeHashEmpty, PasswordEmpty, PasswordRecoveryNa
)
from pyrogram.raw.base.auth import PasswordRecovery
from pyrogram.types import User
import logging
from enum import Enum, StrEnum

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database.core.database import connection
from src.common.database.models.enums import TelegramAccountStatus
from src.common.database.models.user import TelegramAccount
from src.common.utils.auth import AuthResponseStatus
from src.pyrogram.config import settings
from src.common.database.dao.user import TelegramAccountDAO
from src.pyrogram.logger import get_pg_client_logger
from src.pyrogram.services.singleton import BaseSingleton

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AccountStatus(Enum):
    ACTIVE = "active"  # Активен и работает
    INACTIVE = "inactive"  # Не активен (остановлен)
    AUTH_NEEDED = "auth_needed"  # Требуется авторизация
    BANNED = "banned"  # Забанен
    LIMITED = "limited"  # Ограничен (flood wait)
    ERROR = "error"  # Ошибка


class AccountInfo:
    def __init__(self, db_id: int, client_id: str, status: AccountStatus, phone: str):
        self.id = db_id
        self.client_id = client_id
        self.status = AccountStatus.AUTH_NEEDED
        self.phone = phone




class AuthResponse:
    def __init__(
            self, status: AuthResponseStatus, tg_account_id: int | None = None, data: dict[str, Any] | None = None
    ):
        self.status = status
        self.data = data
        self.tg_account_id = tg_account_id

        if data:
            self.data["tg_account_id"] = self.tg_account_id
        else:
            self.data = {"tg_account_id": self.tg_account_id}


class AccountManager(BaseSingleton):



    def __init__(self):
        self.sessions_dir = Path(settings.SESSION_DIR)

        self.accounts_info: Dict[str, AccountInfo] = {}
        self.clients: Dict[str, Client] = {}

        self.sessions_dir.mkdir(exist_ok=True)

    def remove_account(self, name: str):
        if name in self.clients:
            # Останавливаем клиент
            asyncio.create_task(self.stop_account(name))


        # Удаляем файл сессии
        session_file = self.sessions_dir / f"{name}.session"
        if session_file.exists():
            session_file.unlink()

        logger.info(f"➖ Аккаунт {name} удален")

    @connection
    async def new_phone_auth(self, phone: str, db_session: AsyncSession, *args) -> AuthResponse:

        account = await TelegramAccountDAO.get_account_by_phone(db_session=db_session, phone=phone)

        if not account:
            account: TelegramAccount = await TelegramAccountDAO.add(
                session=db_session,
                phone_number=phone
            )

        client_id = account.client_id

        if account.status != TelegramAccountStatus.AUTH_NEEDED:
            return AuthResponse(AuthResponseStatus.PHONE_ALREADY_AUTH, account.id)
        else:
            if client_id in self.clients:
                client = self.clients.get(client_id)
            else:
                client = Client(
                    name=client_id,
                    api_id=settings.API_ID,
                    api_hash=settings.API_HASH,
                    workdir=str(self.sessions_dir),
                    phone_number=phone
                )
                self.clients[client_id] = client

            if await self.check_client_availability(client):
                account.status = TelegramAccountStatus.ACTIVE
                await db_session.commit()
                return AuthResponse(AuthResponseStatus.PHONE_ALREADY_AUTH, account.id)
            else:
                try:

                    sent_code = await client.send_code(
                        phone_number=phone
                    )
                    account.code_hash = sent_code.phone_code_hash
                    await db_session.commit()

                    return AuthResponse(AuthResponseStatus.WAITING_CODE, account.id)
                except (PhoneNumberInvalid, PhoneNumberBanned, PhoneNumberOccupied):
                    await TelegramAccountDAO.delete_obj(session=db_session, obj_id=account.id)
                    return AuthResponse(AuthResponseStatus.INVALID_PHONE)

                except (FloodWait, PhoneNumberFlood) as e:
                    get_pg_client_logger().info(
                        f"Account with phone number {phone} was muted by FloodWait"
                    )
                    return AuthResponse(AuthResponseStatus.FLOOD_WAIT, account.id, data={"wait": e.value})
                except ApiIdInvalid as e:
                    get_pg_client_logger().error(
                        "APi id is invalid"
                    )
                    return AuthResponse(AuthResponseStatus.UNEXPECTED_ERROR, account.id)

    @connection
    async def set_code(self, tg_account_id: int, code: str, db_session: AsyncSession, *args) -> AuthResponse:
        tg_account: TelegramAccount = await TelegramAccountDAO.get_obj(session=db_session, id=tg_account_id)

        if not tg_account:
            return AuthResponse(AuthResponseStatus.UNEXPECTED_ERROR)

        client_id = tg_account.client_id
        client = self.clients.get(client_id)

        if client:
            try:
                user = await client.sign_in(
                    phone_number=tg_account.phone_number,
                    phone_code_hash=tg_account.code_hash,
                    phone_code=code
                )

                await self.setup_account(
                    client=client,
                    tg_account=tg_account,
                    db_session=db_session
                )

                return AuthResponse(AuthResponseStatus.SUCCESS)

            except PhoneCodeInvalid:
                return AuthResponse(AuthResponseStatus.INVALID_CODE)
            except PhoneCodeExpired:
                return AuthResponse(AuthResponseStatus.EXPIRED)

            except SessionPasswordNeeded:
                return AuthResponse(AuthResponseStatus.WAITING_PASSWORD)

            except PhoneCodeHashEmpty:
                get_pg_client_logger().error(
                    f"Invalid hash in client {client}"
                )
                return AuthResponse(AuthResponseStatus.UNEXPECTED_ERROR)

            except FloodWait as e:
                get_pg_client_logger().info(
                        f"Account with phone number {tg_account.phone_number} was muted by FloodWait"
                    )
                return AuthResponse(AuthResponseStatus.FLOOD_WAIT)

        else:
            return AuthResponse(AuthResponseStatus.UNEXPECTED_ERROR)

    @connection
    async def set_password(self, account_id: int, password: str, db_session: AsyncSession, *args):
        tg_account: TelegramAccount = await TelegramAccountDAO.get_obj(session=db_session, id=account_id)

        if not tg_account:
            return AuthResponse(AuthResponseStatus.UNEXPECTED_ERROR)

        client_id = tg_account.client_id
        client = self.clients.get(client_id)

        if client:
            try:
                await client.check_password(
                    password=password
                )
                me = await client.get_me()

                await self.setup_account(
                    client=client,
                    tg_account=tg_account,
                    db_session=db_session
                )

                return AuthResponse(AuthResponseStatus.SUCCESS)
            except (PasswordHashInvalid, PasswordEmpty, PasswordRecoveryNa):
                return AuthResponse(AuthResponseStatus.INVALID_PASSWORD)
        else:
            return AuthResponse(AuthResponseStatus.UNEXPECTED_ERROR)


    async def setup_account(self, client, tg_account: TelegramAccount, db_session: AsyncSession):
        tg_account.status = TelegramAccountStatus.ACTIVE
        # handlers

        await db_session.commit()


    async def stop_client(self, client):
        if client.is_connected:
            await client.stop()


    async def stop_all_accounts(self):
        for client_id, client in self.clients.items():
            await self.stop_client(client)

    async def check_client_availability(self, client: Client) -> bool:
        """
        :param client:
        :return: True - if account auth and ready to work, False - if auth needed
        """
        try:
            await client.connect()

            try:
                me = await client.get_me()

                return True

            except (AuthKeyInvalid, AuthKeyUnregistered, SessionRevoked,):
                return False
        except (ApiIdInvalid,):
            get_pg_client_logger().info(
                "Invalid API ID in config"
            )
            return False
        except Exception as e:
            get_pg_client_logger().info(
                str(e) + "\n" + str(e.args)
            )
            return False


    async def stop_account(self, name: str):
        """Остановка конкретного аккаунта"""
        if name in self.clients:
            try:
                await self.clients[name].disconnect()
                del self.clients[name]

                info = self.accounts_info[name]
                info.status = AccountStatus.INACTIVE
                self._save_accounts_data()

                logger.info(f"🛑 Аккаунт {name} остановлен")
                self._notify_status_change(name, AccountStatus.INACTIVE)

            except Exception as e:
                logger.error(f"Ошибка при остановке {name}: {e}")
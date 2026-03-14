import asyncio
import json
import uuid
from typing import Dict, Any

from asyncio.futures import Future

import redis.asyncio as redis

from src.aiogram_bot.services.data.utils import AuthSessionResult
from src.aiogram_bot.services.singleton import BaseSingleton
from src.common.utils.auth import AuthResponseStatus, GroupAddResponseStatus
from src.pyrogram.logger import get_rcp_logger


class PyrogramAppProcedureCall(BaseSingleton):
    PHONE_AUTH_REQ_STREAM = "phone_auth.requests"
    PHONE_AUTH_RES_STREAM = "phone_auth.responses"
    GROUP_MANAGE_REQ_STREAM = "group.requests"
    GROUP_MANAGE_RES_STREAM = "group.responses"


    def __init__(self, redis_client: redis.Redis = None):
        self.redis_client = redis.Redis(decode_responses=True)

        self.pending: Dict[str, Future] = {}


    async def create_response_loops(self):
        asyncio.create_task(self.response_loop(self.PHONE_AUTH_RES_STREAM))
        asyncio.create_task(self.response_loop(self.GROUP_MANAGE_RES_STREAM))

    async def create_authorize_task(self, phone_number: str) -> AuthSessionResult:
        result = await self.__add_task(
            self.PHONE_AUTH_REQ_STREAM,
            task_type="set_phone",
            data={
                "phone": phone_number,
            }
        )

        status_id = result.get("status")


        if status_id:
            status = AuthResponseStatus(status_id)

            return AuthSessionResult(status, result.get("tg_account_id"))

        else:
            return AuthSessionResult(AuthResponseStatus.UNEXPECTED_ERROR)

    async def send_code_to_authorize(self, code: str, tg_account_id: int) -> AuthSessionResult:
        result = await self.__add_task(
            channel=self.PHONE_AUTH_REQ_STREAM,
            task_type="set_code",
            data={
                "code": code,
                "tg_account_id": tg_account_id
            }
        )

        status_id = result.get("status")

        if status_id:
            status = AuthResponseStatus(status_id)

            return AuthSessionResult(status)
        else:
            get_rcp_logger().error(
                "Pyrogram's RCP didn't send auth response status on sending code stage"
            )
            return AuthSessionResult(AuthResponseStatus.UNEXPECTED_ERROR)


    async def send_password_to_authorize(self, password: str, tg_account_id: int):
        result = await self.__add_task(
            channel=self.PHONE_AUTH_REQ_STREAM,
            task_type="set_password",
            data={
                "password": password,
                "tg_account_id": tg_account_id
            }
        )

        status_id = result.get("status")

        if status_id:
            status = AuthResponseStatus(status_id)

            return AuthSessionResult(status)
        else:
            get_rcp_logger().error(
                "Pyrogram's RCP didn't send auth response status on sending password stage"
            )
            return AuthSessionResult(AuthResponseStatus.UNEXPECTED_ERROR)

    async def check_group(self, tg_account_id: int, group_chat_id: int) -> GroupAddResponseStatus:
        response = await self.__add_task(
            channel=self.GROUP_MANAGE_REQ_STREAM,
            task_type="check_group",
            data={
                "chat_id": group_chat_id,
                "tg_account_id": tg_account_id
            }
        )

        status_id = response.get("status")

        if status_id:

            return GroupAddResponseStatus(status_id)
        else:
            get_rcp_logger().error(
                "Pyrogram's RCP didn't send group add response status"
            )
            return GroupAddResponseStatus.UNEXPECTED

    async def __add_task(self, channel: str, task_type: str, data: dict[str, Any]):
        request_id = str(uuid.uuid4())
        future = asyncio.get_event_loop().create_future()
        self.pending[request_id] = future


        await self.redis_client.xadd(
            channel,
            {
                "request_id": request_id,
                "type": task_type,
                "payload": json.dumps(data)
            }
        )


        return await asyncio.wait_for(future, None)

    async def response_loop(self, channel: str):
        last_id = "$"
        while True:
            messages = await self.redis_client.xread(
                {channel: last_id},
                count=1,
                block=0
            )

            for stream, msgs in messages:
                for msg_id, data in msgs:
                    request_id = data["request_id"]
                    print(request_id, data["payload"])

                    if request_id in self.pending:
                        future = self.pending.pop(request_id)
                        future.set_result(json.loads(data["payload"]))

                    last_id = msg_id

import asyncio
import json

import redis.asyncio as redis

from src.pyrogram.logger import get_rcp_logger
from src.pyrogram.services.app_messaging.dispatcher import TaskDispatcher
from src.pyrogram.services.singleton import BaseSingleton


class PyrogramAppProcedureCall(BaseSingleton):
    PHONE_AUTH_REQ_STREAM = "phone_auth.requests"
    PHONE_AUTH_RES_STREAM = "phone_auth.responses"

    def __init__(self):
        self.redis_client = redis.Redis(decode_responses=True)

    async def run_default_workers(self):
        try:
            await self.redis_client.xgroup_create(
                name=self.PHONE_AUTH_REQ_STREAM,
                groupname="phone_auth_workers",
                id="0",
                mkstream=True
            )
        except redis.ResponseError as e:
            pass

        await asyncio.gather(
            self.worker(
                stream=self.PHONE_AUTH_REQ_STREAM,
                response_stream=self.PHONE_AUTH_RES_STREAM,
                group_name="phone_auth_workers",
                consumer_name="worker-1"
            )
        )

    async def worker(
            self, stream: str, response_stream: str, group_name: str, consumer_name: str
    ):
        try:
            await self.redis_client.xgroup_create(stream, group_name, id="0", mkstream=True)
        except:
            pass

        while True:
            messages = await self.redis_client.xreadgroup(
                groupname=group_name,
                consumername=consumer_name,
                streams={stream: ">"},
                count=1,
                block=0
            )

            for stream, msgs in messages:
                for msg_id, data in msgs:

                    result = await TaskDispatcher.get_instance().dispatch(stream, data)

                    get_rcp_logger().info(
                        f"RCP response: {result}"
                    )

                    await self.redis_client.xadd(
                        response_stream,
                        {
                            "request_id": data.get("request_id"),
                            "payload": json.dumps(result),
                        }
                    )

                    await self.redis_client.xack(stream, group_name, msg_id)

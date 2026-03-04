import redis.asyncio as redis


class PyrogramAppProcedureCall:
    PHONE_AUTH_REQ_STREAM = "phone_auth_requests"
    PHONE_AUTH_RES_STREAM = "phone_auth_responses"


    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client


    async def create_authorize_task(self, phone_number: str):
        await self.__add_task(
            self.PHONE_AUTH_REQ_STREAM,
            {
                    "type": "send_code",
                    "phone": phone_number,
            }
        )


    async def __add_task(self, channel: str, payload):
        await self.redis_client.xadd(
            channel,
            payload
        )

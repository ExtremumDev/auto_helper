

class BaseRemoteProcedureCaller:



    async def __add_task(self, channel: str, payload):
        await self.redis_client.xadd(
            channel,
            payload
        )


import redis


class PyrogramAppProcedureCall:

    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    async def worker(self):
        try:
            await self.redis_client.xgroup_create(STREAM, GROUP, id="0", mkstream=True)
        except:
            pass

        while True:
            messages = await self.redis_client.xreadgroup(
                GROUP,
                CONSUMER,
                {STREAM: ">"},
                count=1,
                block=0  # ждать бесконечно
            )

            for stream, msgs in messages:
                for msg_id, data in msgs:
                    result = await handle(data)

                    await r.xadd(
                        "service.responses",
                        {
                            "request_id": data["request_id"],
                            "payload": json.dumps(result),
                        }
                    )

                    await r.xack(STREAM, GROUP, msg_id)



class TaskDispatcher:


    async def dispatch(self, channel_name: str, data: dict[]):
        task_type = data.get["type"]

        if channel_name == "phone_requests":
            if task_type == "set_phone":
                pass
            elif data == "":
                pass

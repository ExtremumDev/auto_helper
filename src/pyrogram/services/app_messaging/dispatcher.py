from typing import Any

import json

from src.common.utils.auth import AuthResponseStatus
from src.pyrogram.logger import get_rcp_logger
from src.pyrogram.services.auth.client_manager import AccountManager
from src.pyrogram.services.singleton import BaseSingleton


class TaskDispatcher(BaseSingleton):

    async def dispatch(self, channel_name: str, data: dict[str, Any]):
        """
        :param channel_name:
        :param data:
        :return: data for response
        """
        task_type = data.get("type")
        payload = json.loads(data.get("payload"))

        if channel_name == "phone_auth.requests":
            if task_type == "set_phone":
                phone_number = payload.get("phone")

                if phone_number:
                    res = await AccountManager.get_instance().new_phone_auth(phone=phone_number)
                    data = res.data

                    return {
                        "status": res.status.value,
                        **data
                    }
                else:
                    return {
                        "status": AuthResponseStatus.UNEXPECTED_ERROR,
                    }
            elif task_type == "set_code":
                code = payload.get("code")
                tg_account_id = payload.get("tg_account_id")

                if code and tg_account_id:
                    res = await AccountManager.get_instance().set_code(
                        tg_account_id=tg_account_id,
                        code=code
                    )

                    return {
                        "status": res.status.value,
                        **res.data
                    }
                else:
                    get_rcp_logger().error(
                        "Hash code or telegram account id is empty in providing code procedure"
                    )
                    return {
                        "status": AuthResponseStatus.UNEXPECTED_ERROR
                    }
            elif task_type == "set_password":
                password = payload.get("password")
                tg_account_id = payload.get("tg_account_id")

                if password and tg_account_id:
                    res = await AccountManager.get_instance().set_password(
                        password=password,
                        account_id=tg_account_id
                    )

                    return {
                        "status": res.status.value,
                        **res.data
                    }
                else:
                    get_rcp_logger().error(
                        "Password or telegram account id is empty in providing password procedure"
                    )
                    return {
                        "status": AuthResponseStatus.UNEXPECTED_ERROR
                    }

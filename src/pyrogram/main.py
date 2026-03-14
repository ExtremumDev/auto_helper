import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import asyncio


from src.pyrogram.logger import setup_logger

from src.pyrogram.services.app_messaging.rcp import PyrogramAppProcedureCall
from src.pyrogram.services.auth.client_manager import AccountManager
from src.pyrogram.services.app_messaging.dispatcher import TaskDispatcher

def create_services():
    AccountManager.create_instance()
    TaskDispatcher.create_instance()
    PyrogramAppProcedureCall.create_instance()

async def main():
    setup_logger()

    create_services()
    await AccountManager.get_instance().start_all_clients()

    await PyrogramAppProcedureCall.get_instance().run_default_workers()



if __name__ == "__main__":
    asyncio.run(main())

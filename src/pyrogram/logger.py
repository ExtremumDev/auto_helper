from datetime import datetime

import logging

import os

from pathlib import Path


def setup_logger() -> None:
    os.makedirs('logging/RCP', exist_ok=True)
    os.makedirs("logging/pyrogram_clients", exist_ok=True)
    os.makedirs("logging/rcp", exist_ok=True)

    logging_dir = Path(__file__).parent.parent.parent / "logging"

    cur_date = datetime.today().date()

    logging.basicConfig(
        level=logging.INFO,
        filename=logging_dir / f"{cur_date}.log",
        filemode='a+',
        format="%(name)s %(asctime)s %(levelname)s %(message)s",
    )

    logging.getLogger("rcp").addHandler(
        logging.FileHandler(
            filename=logging_dir / f"rcp/{cur_date}.log",
            mode="a+",
            encoding="utf-8"
        )
    )

    logging.getLogger("pyrogram_clients").addHandler(
        logging.FileHandler(
            filename=logging_dir / f"pyrogram_clients/{cur_date}.log",
            mode="a+",
            encoding="utf-8"
        )
    )

    logging.getLogger("pyrogram_clients").addHandler(logging.StreamHandler())

def get_rcp_logger():
    return logging.getLogger("rcp")

def get_pg_client_logger():
    return logging.getLogger("pyrogram_clients")
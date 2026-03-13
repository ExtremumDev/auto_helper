import datetime
import logging
import os
from pathlib import Path


def setup_logger():
    os.makedirs("logging/bot", exist_ok=True)

    logging_dir = Path(__file__).parent.parent.parent / "logging"

    cur_date = datetime.datetime.today().date()

    logging.basicConfig(
        level=logging.INFO,
        filename=logging_dir / f"{cur_date}.log",
        filemode='a+',
        format="%(name)s %(asctime)s %(levelname)s %(message)s",
    )

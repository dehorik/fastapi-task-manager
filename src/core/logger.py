import logging
import os
from logging.handlers import RotatingFileHandler

from core.config import BASE_DIR


LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE_NAME = "logs.log"
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE_NAME)

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
MAX_LOG_FILE_SIZE = 5 * 1024 * 1024
BACKUP_COUNT = 5


def get_logger(name: str = "app") -> logging.Logger:
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)

    roating_file_handler = RotatingFileHandler(
        filename=LOG_FILE_PATH,
        mode="a",
        maxBytes=MAX_LOG_FILE_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    roating_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    new_logger = logging.getLogger(name)
    new_logger.addHandler(roating_file_handler)
    new_logger.setLevel(LOG_LEVEL)

    return new_logger


logger = get_logger()

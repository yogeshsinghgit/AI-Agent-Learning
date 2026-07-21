import sys

from loguru import logger

from app.core.config import settings
from app.core.constants import (
    LOG_COMPRESSION,
    LOG_DIR,
    LOG_FILE_NAME,
    LOG_RETENTION,
    LOG_ROTATION,
)


def configure_logging() -> None:
    """
    Configure Loguru logging.
    """

    LOG_DIR.mkdir(exist_ok=True)

    logger.remove()

    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        enqueue=True,
        backtrace=True,
        diagnose=True,
        colorize=True,
    )

    logger.add(
        LOG_DIR / LOG_FILE_NAME,
        level=settings.LOG_LEVEL,
        rotation=LOG_ROTATION,
        retention=LOG_RETENTION,
        compression=LOG_COMPRESSION,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    logger.info("Logging initialized successfully.")
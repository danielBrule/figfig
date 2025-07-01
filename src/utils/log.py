import os
import logging
from datetime import datetime

DEFAULT_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DEFAULT_LOG_DATETIME_FORMAT = "%Y%m%d-%H%M%S"
DEFAULT_LOG_FILE_PATH = "/home/LogFiles/app-[DATETIME_PLACEHOLDER].log"

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", DEFAULT_LOG_FILE_PATH)
LOG_DATETIME_FORMAT = os.getenv("LOG_DATETIME_FORMAT", DEFAULT_LOG_DATETIME_FORMAT)
LOG_FORMAT = os.getenv("LOG_FORMAT", DEFAULT_LOG_FORMAT)


def compute_log_file_path(log_file_path: str, log_datetime_format: str) -> str:
    if "[DATETIME_PLACEHOLDER]" not in log_file_path:
        raise ValueError("LOG_FILE_PATH must include [DATETIME_PLACEHOLDER]")
    return log_file_path.replace(
        "[DATETIME_PLACEHOLDER]",
        datetime.now().strftime(log_datetime_format)
    )


def create_logger(
    log_format: str = DEFAULT_LOG_FORMAT,
    log_file_path: str | None = None,
    log_datetime_format: str = DEFAULT_LOG_DATETIME_FORMAT,
    log_level: int = logging.INFO
) -> logging.Logger:
    logger_ = logging.getLogger(__name__)
    logger_.setLevel(log_level)
    logger_.propagate = False

    # Avoid adding duplicate handlers
    if logger_.handlers:
        return logger_

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    logger_.addHandler(console_handler)

    # File handler if needed
    if log_file_path:
        try:
            full_log_path = compute_log_file_path(log_file_path, log_datetime_format)
            os.makedirs(os.path.dirname(full_log_path), exist_ok=True)
            file_handler = logging.FileHandler(full_log_path, mode="a+", encoding="utf-8")
            file_handler.setLevel(log_level)
            file_handler.setFormatter(logging.Formatter(log_format))
            logger_.addHandler(file_handler)
        except Exception as e:
            logger_.error(f"Failed to set up file logging: {e}")

    logger_.info("Logger initialized")
    logger_.info(f"\tLOG_FORMAT: {LOG_FORMAT}")
    logger_.info(f"\tLOG_FILE_PATH: {LOG_FILE_PATH}")

    return logger_


# Configure root logger
logging.getLogger("sqlalchemy").setLevel(logging.ERROR)
root_logger = logging.getLogger()
root_logger.handlers.clear()
root_logger.propagate = False

# Your main logger
logger = create_logger(
    log_format=LOG_FORMAT,
    log_file_path=LOG_FILE_PATH,
    log_datetime_format=LOG_DATETIME_FORMAT,
    log_level=logging.INFO
)


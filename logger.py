from datetime import datetime
from loguru import logger


def init_logger():
    logger.add(f"file_{datetime.now().strftime('%d_%m')}.log", rotation='20mb')


def log_msg(level: str, msg: str):
    """
    Logging with loguru

    :param level: Type of log
    :param msg: Log message
    """
    log_type = {
        'warning': logger.warning,
        'info': logger.info,
        'success': logger.success
    }
    log_type[level](msg)

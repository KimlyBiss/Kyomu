import logging
from colorlog import ColoredFormatter

# Глобальный объект логгера
logger = logging.getLogger('KYOMU')

def setup_logger() -> logging.Logger:
    """Инициализация цветного логгера для всего проекта"""
    global logger
    
    if logger.handlers:
        return logger

    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s %(levelname)-8s%(reset)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger

# Инициализация при импорте
setup_logger()

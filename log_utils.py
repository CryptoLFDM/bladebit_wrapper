import logging
import colorlog

DEFAULT = 1
INFO = 2
SUCCESS = 3
HIGHLIGHT = 4
WARNING = 5
FAILED = 6
logging.addLevelName(DEFAULT, 'INFO')
logging.addLevelName(INFO, 'INFO')
logging.addLevelName(SUCCESS, 'SUCCESS')
logging.addLevelName(HIGHLIGHT, 'HIGHLIGHT')
logging.addLevelName(WARNING, 'WARNING')
logging.addLevelName(FAILED, 'FAILED')
color_mapping = {
    'DEFAULT': 'grey',
    'INFO': 'cyan',
    'SUCCESS': 'green',
    'HIGHLIGHT': 'yellow',
    'WARNING': 'purple',
    'FAILED': 'red'
}
log_pattern = '%(asctime)s %(log_color)s%(levelname)s%(reset)s | %(name)s | %(log_color)s%(message)s'
formatter = colorlog.ColoredFormatter(log_pattern, log_colors=color_mapping)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger('bladebit-wrapper')
logger.addHandler(handler)
logger.setLevel(DEFAULT)
chia_logger = logging.getLogger('chia.plotters.bladebit')
chia_logger.addHandler(handler)


def log_info(msg: any):
    logger.log(INFO, msg)


def log_success(msg: any):
    logger.log(SUCCESS, msg)


def log_failed(msg: any):
    logger.log(FAILED, msg)


def log_warning(msg: any):
    logger.log(WARNING, msg)

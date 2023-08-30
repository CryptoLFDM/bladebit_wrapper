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

bladebit_plotter_logger = logging.getLogger('bladebit.wrapper.plotter')
bladebit_plotter_logger.addHandler(handler)
bladebit_plotter_logger.setLevel(DEFAULT)

bladebit_manager_logger = logging.getLogger('bladebit.wrapper.manager')
bladebit_manager_logger.addHandler(handler)
bladebit_manager_logger.setLevel(DEFAULT)

bladebit_wrapper_logger = logging.getLogger('bladebit.wrapper')
bladebit_wrapper_logger.addHandler(handler)
bladebit_wrapper_logger.setLevel(DEFAULT)

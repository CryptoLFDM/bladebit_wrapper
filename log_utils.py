import logging
import colorlog

global Logger


class LoggerUtils:
    DEBUG = 1
    INFO = 2
    SUCCESS = 3
    HIGHLIGHT = 4
    WARNING = 5
    FAILED = 6

    def __init__(self, debug: bool):
        logging.addLevelName(self.DEBUG, 'DEBUG')
        logging.addLevelName(self.INFO, 'INFO')
        logging.addLevelName(self.SUCCESS, 'SUCCESS')
        logging.addLevelName(self.HIGHLIGHT, 'HIGHLIGHT')
        logging.addLevelName(self.WARNING, 'WARNING')
        logging.addLevelName(self.FAILED, 'FAILED')
        color_mapping = {
            'DEBUG': 'orange',
            'DEFAULT': 'grey',
            'INFO': 'cyan',
            'SUCCESS': 'green',
            'HIGHLIGHT': 'yellow',
            'WARNING': 'purple',
            'FAILED': 'red'
        }
        if debug:
            log_pattern = '%(asctime)s %(log_color)s%(levelname)s%(reset)s [%(filename)s:%(lineno)s - %(funcName)20s() ] | %(name)s | %(log_color)s%(message)s'
            level = self.DEBUG
        else:
            log_pattern = '%(asctime)s %(log_color)s%(levelname)s%(reset)s | %(name)s | %(log_color)s%(message)s'
            level = self.INFO

        self.formatter = colorlog.ColoredFormatter(log_pattern, log_colors=color_mapping)
        self.handler = logging.StreamHandler()
        self.handler.setFormatter(self.formatter)

        self.bladebit_plotter_logger = logging.getLogger('bladebit.wrapper.plotter')
        self.bladebit_plotter_logger.addHandler(self.handler)
        self.bladebit_plotter_logger.setLevel(level)

        self.bladebit_manager_logger = logging.getLogger('bladebit.wrapper.manager')
        self.bladebit_manager_logger.addHandler(self.handler)
        self.bladebit_manager_logger.setLevel(level)

        self.bladebit_wrapper_logger = logging.getLogger('bladebit.wrapper.main')
        self.bladebit_wrapper_logger.addHandler(self.handler)
        self.bladebit_wrapper_logger.setLevel(level)


def init_logger(debug: bool):
    global Logger
    Logger = LoggerUtils(debug)




import os
import re
from pathlib import Path
import time

import config_loader
from log_utils import bladebit_plotter_logger, INFO, WARNING, FAILED, SUCCESS

plot_base_pattern = re.compile('plot-k32-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-.*plot')
plot_compressed_pattern = re.compile('plot-k32-c[0-9]{2}-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-.*plot')


def does_plot_has_lower_compression(plot_name: str) -> bool:
    if plot_base_pattern.match(plot_name):
        bladebit_plotter_logger.log(INFO, '{} is not a compressed plot, going to delete it'.format(plot_name))
        return True
    if plot_compressed_pattern.match(plot_name):
        if plot_name.split('-')[2][:1] < config_loader.config['compression_level']:
            bladebit_plotter_logger.log(INFO, '{} has a lower compression than specified in config, going to delete it'.format(plot_name))
            return True
    bladebit_plotter_logger.log(INFO, 'Nothing to delete here')
    return False


def find_plot_to_destroy() -> Path:
    for disk in config_loader.config['directories_to_plot']:
        files = os.listdir(disk)
        for file in files:
            if does_plot_has_lower_compression(file):
                return Path('{}/{}'.format(disk, file))
    return None


def can_delete_plot(plot_path: Path) -> str:
    try:
        if os.path.isfile(plot_path):
            os.remove(plot_path)
            bladebit_plotter_logger.log(SUCCESS, '{} has been deleted'.format(plot_path))
            time.sleep(0.5)
            return "OK"
    except Exception as e:
        bladebit_plotter_logger.log(FAILED, 'An error occurred: {}'.format(e))
        return None
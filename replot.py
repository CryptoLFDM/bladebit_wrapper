import os
import re
from pathlib import Path
import time

import config_loader
import log_utils as wp

plot_base_pattern = re.compile('plot-k32-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-.*plot')
plot_compressed_pattern = re.compile('plot-k32-c[0-9]{2}-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-.*plot')


def does_plot_has_lower_compression(plot_name: str) -> bool:
    if plot_base_pattern.match(plot_name):
        wp.Logger.bladebit_plotter_logger.log(wp.Logger.INFO, '{} is not a compressed plot, going to delete it'.format(plot_name))
        return True
    if plot_compressed_pattern.match(plot_name):
        if plot_name.split('-')[2][:1] < config_loader.Config.compression_level:
            wp.Logger.bladebit_plotter_logger.log(wp.Logger.INFO, '{} has a lower compression than specified in config, going to delete it'.format(plot_name))
            return True
    wp.Logger.bladebit_plotter_logger.log(wp.Logger.INFO, 'Nothing to delete here')
    return False


def find_plot_to_destroy() -> Path:
    for disk in config_loader.Config.directories_to_plot:
        files = os.listdir(disk)
        for file in files:
            if does_plot_has_lower_compression(file):
                return Path('{}/{}'.format(disk, file))
    return None


def can_delete_plot(plot_path: Path) -> str:
    try:
        if os.path.isfile(plot_path):
            os.remove(plot_path)
            wp.Logger.bladebit_plotter_logger.log(wp.Logger.SUCCESS, '{} has been deleted'.format(plot_path))
            time.sleep(0.5)
            return "OK"
    except Exception as e:
        wp.Logger.bladebit_plotter_logger.log(wp.Logger.FAILED, 'An error occurred: {}'.format(e))
        return None
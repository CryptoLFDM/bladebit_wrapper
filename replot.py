import os
import re
from pathlib import Path
import time

from config import config, chia_const
from log_utils import log_info, log_failed, log_success

plot_base_pattern = re.compile('plot-k32-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-.*plot')
plot_compressed_pattern = re.compile('plot-k32-c[0-9]{2}-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-.*plot')


def does_plot_has_lower_compression(plot_name: str) -> bool:
    if plot_base_pattern.match(plot_name):
        log_info('{} is not a compressed plot, going to delete it'.format(plot_name))
        return True
    if plot_compressed_pattern.match(plot_name):
        if plot_name.split('-')[2][:1] < config['compression_level']:
            log_info('{} has a lower compression than specified in config, going to delete it'.format(plot_name))
            return True
    log_info('Nothing to delete here')
    return False


def find_plot_to_destroy() -> Path:
    for disk in config['directories_to_plot']:
        files = os.listdir(disk)
        for file in files:
            if does_plot_has_lower_compression(file):
                return Path('{}/{}'.format(disk, file))
    return None


def can_delete_plot(plot_path: Path) -> bool:
    try:
        if os.path.isfile(plot_path):
            os.remove(plot_path)
            log_success('{} has been deleted'.format(plot_path))
            time.sleep(0.5)
            return True
    except Exception as e:
        log_failed('An error occurred: {}'.format(e))
        return False
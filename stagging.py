
from config import config, chia_const
from log_utils import bladebit_plotter_logger, INFO, WARNING, FAILED, SUCCESS
from utils import get_disk_info


def get_staging_plot_dir() -> str:
    for staging_disk in config['staging_directories']:
        _, _, free = get_disk_info(staging_disk)
        if free / chia_const[config['compression_level']]['gib'] * 2:
            bladebit_plotter_logger.log(INFO, '{} is candidate for staging disk'.format(staging_disk))
            return staging_disk
    bladebit_plotter_logger.log(WARNING, 'All staging directories are full')
    return None

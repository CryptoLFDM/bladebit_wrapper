
import config_loader
from log_utils import bladebit_plotter_logger, INFO, WARNING, FAILED, SUCCESS
from utils import get_disk_info


def get_staging_plot_dir() -> str:
    for staging_disk in config_loader.config['staging_directories']:
        _, _, free = get_disk_info(staging_disk)
        if free / config_loader.chia_const[config_loader.config['compression_level']]['gib'] * 2:
            bladebit_plotter_logger.log(INFO, '{} is candidate for staging disk'.format(staging_disk))
            return staging_disk
    bladebit_plotter_logger.log(WARNING, 'All staging directories are full')
    return None

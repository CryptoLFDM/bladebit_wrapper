
import config_loader
import log_utils as wp
from utils import get_disk_info


def get_staging_plot_dir() -> str:
    for staging_disk in config_loader.Config.staging_directories:
        _, _, free = get_disk_info(staging_disk)
        if free / config_loader.chia_const[config_loader.Config.compression_level]['gib'] * 2:
            wp.Logger.bladebit_plotter_logger.log(wp.Logger.INFO, '{} is candidate for staging disk'.format(staging_disk))
            return staging_disk
    wp.Logger.bladebit_plotter_logger.log(wp.Logger.WARNING, 'All staging directories are full')
    return None

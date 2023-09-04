import shutil
import pathlib

import log_utils as wp
import config_loader


def print_disk_info(disk_path: str):
    total, used, free = get_disk_info(disk_path)
    wp.Logger.bladebit_plotter_logger.log(wp.Logger.INFO, 'Disk: {}'.format(disk_path))
    wp.Logger.bladebit_plotter_logger.log(wp.Logger.INFO, "\tTotal: {} GiB".format(total))
    wp.Logger.bladebit_plotter_logger.log(wp.Logger.INFO, "\tUsed: {} GiB".format(used))
    wp.Logger.bladebit_plotter_logger.log(wp.Logger.INFO, "\tFree: {} GiB\n".format(free))


def get_disk_info(disk_path: str) -> tuple[float, float, float]:
    total, used, free = shutil.disk_usage(pathlib.Path(disk_path))
    total = total // (2**30)
    used = used // (2**30)
    free = free // (2**30)
    return total, used, free


def can_plot_at_least_one_plot_safely(disk_path: str) -> bool:
    _, _, free = get_disk_info(disk_path)
    if free / config_loader.chia_const[config_loader.Config.compression_level]['gib'] > 2:
        return True
    return False

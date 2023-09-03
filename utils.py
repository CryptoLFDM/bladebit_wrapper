import shutil
import pathlib

from log_utils import bladebit_plotter_logger, INFO, WARNING, FAILED, SUCCESS
import config_loader


def print_disk_info(disk_path: str):
    total, used, free = get_disk_info(disk_path)
    bladebit_plotter_logger.log(INFO, 'Disk: {}'.format(disk_path))
    bladebit_plotter_logger.log(INFO, "\tTotal: {} GiB".format(total))
    bladebit_plotter_logger.log(INFO, "\tUsed: {} GiB".format(used))
    bladebit_plotter_logger.log(INFO, "\tFree: {} GiB\n".format(free))


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

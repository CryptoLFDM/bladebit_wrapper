import shutil
import pathlib

from log_utils import bladebit_plotter_logger, INFO, WARNING, FAILED, SUCCESS


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

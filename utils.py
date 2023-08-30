import shutil
import pathlib

from log_utils import log_info, log_failed, log_success, log_warning


def print_disk_info(disk_path: str):
    total, used, free = get_disk_info(disk_path)
    log_info('Disk: {}'.format(disk_path))
    log_info("\tTotal: {} GiB".format(total))
    log_info("\tUsed: {} GiB".format(used))
    log_info("\tFree: {} GiB\n".format(free))


def get_disk_info(disk_path: str) -> tuple[float, float, float]:
    total, used, free = shutil.disk_usage(pathlib.Path(disk_path))
    total = total // (2**30)
    used = used // (2**30)
    free = free // (2**30)
    return total, used, free
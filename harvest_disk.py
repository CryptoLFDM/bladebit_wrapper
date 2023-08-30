import shutil
import pathlib

from config import config, chia_const
from plot import run_plot
from log_utils import log_info, log_failed, log_success


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


def harvest_all_disk() -> dict:
    free_disk_space = {}
    for disk in config['directories_to_plot']:
        print_disk_info(disk)
        _, _, free_disk_space[disk] = get_disk_info(disk)
    return free_disk_space


def process_disk_plotting(disk_name: str):
    log_success('going to plot on {}'.format(disk_name))
    run_plot(disk_name)


def calculate_plot(disks_info: dict) -> bool:
    for disk_name, disk_info in disks_info.items():
        while disk_info > chia_const[config['compression_level']]['gib']:
            process_disk_plotting(disk_name)
        else:
            log_failed('can\'t plot anymore on {}'.format(disk_name))
    return False

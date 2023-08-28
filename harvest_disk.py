import shutil
import pathlib
import logging

from config import config, chia_const
from plot import run_plot
from log_utils import log_info, log_failed, log_success


def get_disk_info(disk_path: str) -> float:

    total, used, free = shutil.disk_usage(pathlib.Path(disk_path))
    log_info('Disk: {}'.format(disk_path))
    log_info("\tTotal: {} GiB".format(total // (2**30)))
    log_info("\tUsed: {} GiB".format(used // (2**30)))
    log_info("\tFree: {} GiB\n".format(free // (2**30)))
    return free // (2**30)


def harvest_all_disk() -> dict:
    free_disk_space = {}
    for disk in config['directories_to_plot']:
        free_disk_space[disk] = get_disk_info(disk)
    return free_disk_space


def calculate_plot(disks_info: dict) -> bool:
    log_info(disks_info)
    for disk_name, disk_info in disks_info.items():
        log_info(disk_info)
        if disk_info > chia_const[config['compression_level']]['gib']:
            log_success('can print on {}'.format(disk_name))
            run_plot(disk_name)
        else:
            log_failed('can\'t print anymore on {}'.format(disk_name))
    return False


def find_plot_to_destroy(disks_info):
    pass
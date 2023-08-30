from config import config, chia_const
from plot import run_plot
from log_utils import log_info, log_failed, log_success
from utils import get_disk_info, print_disk_info


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

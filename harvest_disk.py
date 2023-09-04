import config_loader
import log_utils as wp
from utils import get_disk_info, print_disk_info, can_plot_at_least_one_plot_safely


def harvest_all_disk() -> dict:
    free_disk_space = {}
    for disk in config_loader.Config.directories_to_plot:
        print_disk_info(disk)
        _, _, free_disk_space[disk] = get_disk_info(disk)
    return free_disk_space


def calculate_plot(disks_info: dict) -> str:
    for disk_name, disk_info in disks_info.items():
        while disk_info > config_loader.chia_const[config_loader.Config.compression_level]['gib'] * 2:
            wp.Logger.bladebit_plotter_logger.log(wp.Logger.SUCCESS, 'going to plot on {}'.format(disk_name))
            if can_plot_at_least_one_plot_safely(disk_name):
                return disk_name
            else:
                wp.Logger.bladebit_plotter_logger.log(wp.Logger.WARNING, 'cannot plot on {} disk have not enough space', disk_name)
        else:
            wp.Logger.bladebit_plotter_logger.log(wp.Logger.FAILED, 'can\'t plot anymore on {}'.format(disk_name))
    return None

import config_loader
from log_utils import bladebit_plotter_logger, INFO, WARNING, FAILED, SUCCESS
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
            bladebit_plotter_logger.log(SUCCESS, 'going to plot on {}'.format(disk_name))
            if can_plot_at_least_one_plot_safely(disk_name):
                return disk_name
            else:
                bladebit_plotter_logger.log(WARNING, 'cannot plot on {} disk have not enough space', disk_name)
        else:
            bladebit_plotter_logger.log(FAILED, 'can\'t plot anymore on {}'.format(disk_name))
    return None

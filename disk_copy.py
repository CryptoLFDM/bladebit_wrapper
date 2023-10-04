import shutil
import os
import time
import threading

import config_loader
import log_utils as wp
from utils import get_disk_info

from sqlite import DBPool

DBPool = DBPool('plot.db')


def left_space_on_directories_to_plots() -> list[str]:
    available_disks = []
    for disk in config_loader.Config.directories_to_plot:
        total, used, free = get_disk_info(disk)
        if free > config_loader.chia_const[config_loader.Config.compression_level]['gib']:
            available_disks.append(disk)
    return available_disks


def scan_plots():
    wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO, 'Scan for new plot in progress')
    for staging_dir in config_loader.Config.staging_directories:
        for filename in os.listdir(staging_dir):
            if filename.endswith('.plot'):
                result = DBPool.insert_new_plot(filename, staging_dir)
    plots = DBPool.get_all_plots()


def move_plot(plot_name, source, destination):
    try:
        source_path = os.path.join(source, plot_name)
        dest_path = os.path.join(destination, plot_name)
        shutil.move(source_path, dest_path)
        return True
    except Exception as e:
        wp.Logger.bladebit_manager_logger.log(wp.Logger.FAILED, 'Error moving {}: {}'.format(plot_name, {str(e)}))
        return False


def process_plots(destination):
    while left_space_on_directories_to_plots():
        scan_plots()
        result = DBPool.get_first_plot_without_status()
        if result and len(result[0]) == 5:
            plot_name, source, _, _, timestamp = result[0]
            with threading.Lock():
                wp.Logger.bladebit_manager_logger.log(wp.Logger.SUCCESS, 'Start copy from {} to {}'.format(source, destination))
                DBPool.update_plot_by_name(str(plot_name), str(destination), 'in_progress')
            if move_plot(plot_name, source, destination):
                with threading.Lock():
                    wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO, 'Moved {} from {} to {}'.format(plot_name, source, destination))
                    DBPool.update_plot_by_name(str(plot_name), str(destination), 'done')
            else:
                wp.Logger.bladebit_manager_logger.log(wp.Logger.FAILED, 'Sleep mode for 5 minutes')
                time.sleep(300)
        else:
            wp.Logger.bladebit_manager_logger.log(wp.Logger.FAILED, 'Sleep mode for 5 minutes')
            time.sleep(300)
    else:
        wp.Logger.bladebit_manager_logger.log(wp.Logger.FAILED, 'No available space on disks')


def plot_manager():
    DBPool.ensure_db_has_not_in_progess_plot_at_start_up()
    wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO, "Going to start plot manager")
    dest_dir = left_space_on_directories_to_plots()
    num_process = 5
    processes = []

    for _ in range(num_process):
        if dest_dir:
            destination = dest_dir.pop(0)
            process = threading.Thread(target=process_plots, args=(destination,))
            processes.append(process)
            process.start()
    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        for process in processes:
            process.join()

import shutil
import os
import time
import threading
from typing import Tuple

import config_loader
import log_utils as wp
from utils import get_disk_info

from sqlite import DBPool

DBPool = DBPool('plot.db')


def get_plot_to_process() -> Tuple[str, str, any, any, float]:
    result = DBPool.get_first_plot_without_status()
    if result and len(result[0]) == 5:
        return result[0]
    else:
        wp.Logger.bladebit_manager_logger.log(wp.Logger.FAILED, 'Sleep mode for 5 minutes')
        time.sleep(300)


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
                _ = DBPool.insert_new_plot(filename, staging_dir)
    _ = DBPool.get_all_plots()


def move_plot(plot_name: str, source: str, destination: str) -> bool:
    chk_plot_name, _, _, _, _ = get_plot_to_process()
    if chk_plot_name is not plot_name:
        wp.Logger.bladebit_manager_logger.log(wp.Logger.FAILED, 'seems {} is already procedeed: new plot in queue is {}'.format(plot_name, chk_plot_name))
        return False
    try:
        source_path = os.path.join(source, plot_name)
        dest_path = os.path.join(destination, plot_name)
        wp.Logger.bladebit_manager_logger.log(wp.Logger.SUCCESS, 'Start copy from {} to {}'.format(source, destination))
        _ = DBPool.update_plot_by_name(str(plot_name), str(destination), 'in_progress')
        shutil.move(source_path, dest_path)
        _ = DBPool.update_plot_by_name(str(plot_name), str(destination), 'done')
        wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO,
                                              'Moved {} from {} to {}'.format(plot_name, source, destination))
        return True

    except Exception as e:
        wp.Logger.bladebit_manager_logger.log(wp.Logger.FAILED, 'Error moving {}: {}'.format(plot_name, {str(e)}))
        _ = DBPool.update_plot_by_name(str(plot_name), str(destination), None)
        return False


def process_plots(destination: str):
    while left_space_on_directories_to_plots():
        scan_plots()
        plot_name, source, _, _, timestamp = get_plot_to_process()
        with threading.Lock():
            move_plot(plot_name, source, destination)
    else:
        wp.Logger.bladebit_manager_logger.log(wp.Logger.FAILED, 'No available space on disks')


def set_concurrent_process() -> int:
    if config_loader.Config.staging_use_process_number:
        return config_loader.Config.staging_copy_concurrent_process
    else:
        return len(config_loader.Config.directories_to_plot)


def plot_manager():
    DBPool.ensure_db_has_not_in_progess_plot_at_start_up()
    wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO, "Going to start plot manager")
    dest_dir = left_space_on_directories_to_plots()
    num_process = set_concurrent_process()
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

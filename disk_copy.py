import shutil
import os
import sys
import concurrent.futures
import random
import time
from typing import Tuple

import config_loader
import log_utils as wp
from utils import get_disk_info, print_disk_info

from sqlite import DBPool

DBPool = DBPool('plot.db')


def get_plot_to_process() -> str:
    result = DBPool.get_first_plot_without_status_and_change_status()
    if result is not None and result.endswith('.plot'):
        return result
    else:
        wp.Logger.bladebit_manager_logger.log(wp.Logger.FAILED, 'Sleep mode for 5 minutes')
        time.sleep(300)
        return None


def left_space_on_directories_to_plots(print_info: bool = None) -> list[str]:
    available_disks = []
    for disk in config_loader.Config.directories_to_plot:
        total, used, free = get_disk_info(disk)
        if free > config_loader.chia_const[config_loader.Config.compression_level]['gib']:
            available_disks.append(disk)
    if print_info:
        wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO, 'Disk list available is {}'.format(available_disks))
    return available_disks


def scan_plots():
    wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO, 'Scan for new plot in progress')
    for staging_dir in config_loader.Config.staging_directories:
        for filename in os.listdir(staging_dir):
            if filename.endswith('.plot'):
                _ = DBPool.insert_new_plot(filename, staging_dir)
    _ = DBPool.get_all_plots()


def move_plot(plot_name: str, source: str, destination: str) -> bool:
    try:
        source_path = os.path.join(source, plot_name)
        dest_path = os.path.join(destination, plot_name)
        wp.Logger.bladebit_manager_logger.log(wp.Logger.SUCCESS, 'Start copy from {} to {}'.format(source, destination))
        _ = DBPool.update_plot_by_name(str(plot_name), str(destination), 'in_progress')
        shutil.move(source_path, dest_path)
        _ = DBPool.update_plot_by_name(str(plot_name), None, 'done')
        wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO,
                                              'Moved {} from {} to {}'.format(plot_name, source, destination))
        return True

    except Exception as e:
        wp.Logger.bladebit_manager_logger.log(wp.Logger.FAILED, 'Error moving {}: {}'.format(plot_name, {str(e)}))
        _ = DBPool.update_plot_by_name(str(plot_name), None, 'to_process')
        return False


def get_first_free_destination(directories: list[str]) -> str:
    dests = DBPool.get_all_destination_by_status('in_progress')
    current_in_progress_copy = sorted([str(t[0]) for t in dests])
    target_dir_list = sorted(directories)
    difference = sorted(list(set(target_dir_list) - set(current_in_progress_copy)))
    if len(difference) > 0:
        wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO, "disk {} has no current copy on, so it will be used".format(difference[0]))
        return difference[0]
    wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO, "All disk currently used, nothing to do")
    return None


def set_concurrent_process() -> int:
    if config_loader.Config.staging_use_process_number:
        wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO,
                                              "Number of thread set to {} from config file".format(config_loader.Config.staging_copy_concurrent_process))
        return config_loader.Config.staging_copy_concurrent_process
    else:
        wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO,
                                              "Number of thread set to {} from destination drive count".format(
                                                  len(config_loader.Config.directories_to_plot)))
        return len(config_loader.Config.directories_to_plot)


def process_plot(name: str):
    scan_plots()
    timer = random.uniform(2, 20)
    wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO, "Thread {} has started with a timer of {} seconds".format(name, timer))
    time.sleep(timer)
    plot_name = get_plot_to_process()
    if plot_name is not None:
        destination = get_first_free_destination(left_space_on_directories_to_plots(True))
        if destination is not None:
            plot_name, source, _, _, _ = DBPool.get_plot_by_name(plot_name)
            move_plot(plot_name, source, destination)
        else:
            wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO, "No available destination  found")
    else:
        wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO, "No available plot found")
    wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO, "Thread {} has finished after {} seconds".format(name, timer))


def plot_manager():
    DBPool.ensure_db_has_not_in_progess_plot_at_start_up()
    wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO, "Going to start plot manager")
    try:
        thread_id = 1
        directories = left_space_on_directories_to_plots()
        max_thread = set_concurrent_process()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_thread) as executor:
            while len(directories) > 0:
                directories = left_space_on_directories_to_plots()
                executor.submit(process_plot, "Moove-{}".format(thread_id))
                thread_id += 1
    except KeyboardInterrupt as e:
        sys.exit(e)
    except Exception as e:
        wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO, "Error {}".format(e))
import shutil
import os
import sys
import concurrent.futures
import random
import time
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
        _ = DBPool.update_plot_by_name(str(plot_name), None, None)
        return False


def get_first_free_destination():
    dest = DBPool.get_all_destination_by_status('in_progres')
    for tpl in dest:
        if tpl[0] not in config_loader.Config.directories_to_plot:
            return tpl[0]
    return None


def set_concurrent_process() -> int:
    if config_loader.Config.staging_use_process_number:
        return config_loader.Config.staging_copy_concurrent_process
    else:
        return len(config_loader.Config.directories_to_plot)


def process_plot(name):
    scan_plots()
    timer = random.uniform(2, 20)
    print("Thread {} has started with a timer of {} seconds".format(name, timer))
    time.sleep(timer)
    plot_name, source, _, _, _ = get_plot_to_process()
    destination = get_first_free_destination()
    if destination is not None:
        move_plot(plot_name, source, destination)
    print("Thread {} has finished after {} seconds".format(name, timer))


def plot_manager():
    DBPool.ensure_db_has_not_in_progess_plot_at_start_up()
    wp.Logger.bladebit_manager_logger.log(wp.Logger.INFO, "Going to start plot manager")

    try:
        thread_id = 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=set_concurrent_process()) as executor:
            while left_space_on_directories_to_plots() is not []:
                executor.submit(process_plot, "Moove-{}".format(thread_id))
                thread_id += 1
    except KeyboardInterrupt as e:
        sys.exit(e)
    except Exception as e:
        wp.Logger.bladebit_manager_logger.log(wp.Logger.FAILED, "Error {}".format(e))
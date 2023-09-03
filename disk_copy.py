import shutil
import os
import time
import threading

import config_loader
from log_utils import bladebit_manager_logger, INFO, WARNING, FAILED, SUCCESS
from utils import can_plot_at_least_one_plot_safely

from sqlite import DBPool

DBPool = DBPool()


def left_space_on_directories_to_plots() -> bool:
    for disk in config_loader.Config.directories_to_plot:
        if can_plot_at_least_one_plot_safely(disk):
            return True
    return False


def scan_plots():
    bladebit_manager_logger.log(INFO, 'Scan for new plot in progress')
    for staging_dir in config_loader.Config.staging_directories:
        for filename in os.listdir(staging_dir):
            if filename.endswith('.plot'):
                DBPool.insert_new_plot(filename, staging_dir)




def process_plots(destination):
    while left_space_on_directories_to_plots():
        scan_plots()
        try:
            result = DBPool.get_first_plot_without_status()
            if result:
                plot_name, source, _, _ = result
                DBPool.update_plot_by_name(plot_name, destination, 'in_progress')
                source_path = os.path.join(source, plot_name)
                dest_path = os.path.join(destination, plot_name)
                shutil.move(source_path, dest_path)
                with threading.Lock():
                    bladebit_manager_logger.log(INFO, 'Moved {} from {} to {}'.format(plot_name, source, dest_path))
                    DBPool.update_plot_by_name(plot_name, destination, 'done')
            else:
                bladebit_manager_logger.log(FAILED, 'Sleep mode for 5 minutes')
                time.sleep(300)
        except Exception as e:
            bladebit_manager_logger.log(FAILED, str(e))
            time.sleep(300)


def plot_manager():
    DBPool.ensure_db_has_not_in_progess_plot_at_start_up()
    bladebit_manager_logger.log(INFO, "Going to start plot manager")
    dest_dir = config_loader.Config.directories_to_plot
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

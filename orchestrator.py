import threading

from log_utils import bladebit_wrapper_logger, INFO, WARNING, FAILED, SUCCESS
from disk_copy import plot_manager
from plot import plot_runner
import config_loader


def bladebit_wrapper_orchestrator():
    processes = []

    if config_loader.Config.plotter_enabled:
        bladebit_wrapper_logger.log(INFO, 'Create process for plotter')
        plot_runner_process = threading.Thread(target=plot_runner)
        plot_runner_process.start()
        processes.append(plot_runner_process)
    if config_loader.Config.use_staging_directories:
        bladebit_wrapper_logger.log(INFO, 'Create process for plot manager')
        plot_manager_process = threading.Thread(target=plot_manager)
        plot_manager_process.start()
        processes.append(plot_manager_process)
    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        for process in processes:
            process.join()

    bladebit_wrapper_logger.log(INFO, "All Process done, going to exit")
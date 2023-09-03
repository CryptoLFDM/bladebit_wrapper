import multiprocessing

from log_utils import bladebit_wrapper_logger, INFO, WARNING, FAILED, SUCCESS
from disk_copy import plot_manager
from plot import plot_runner
from config import config


def bladebit_wrapper_orchestrator():
    if config['plotter_enabled']:
        bladebit_wrapper_logger.log(INFO, 'Create process for plotter')
        plot_runner_process = multiprocessing.Process(target=plot_runner)
        plot_runner_process.start()
        plot_runner_process.join()

    if config['use_staging_directories']:
        bladebit_wrapper_logger.log(INFO, 'Create process for plot manager')
        plot_manager_process = multiprocessing.Process(target=plot_manager)
        plot_manager_process.start()
        plot_manager_process.join()

    bladebit_wrapper_logger.log(INFO, "All Process done, going to exit")
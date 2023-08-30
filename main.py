import multiprocessing

from harvest_disk import harvest_all_disk, calculate_plot
from replot import can_delete_plot, find_plot_to_destroy
from config import config
from log_utils import log_info, log_failed, log_success
from disk_copy import start_copy

def plot_runner():
    circuit_breaker = True
    while circuit_breaker:
        disk_space = harvest_all_disk()
        circuit_breaker = calculate_plot(disk_space)
        if config['mode'] == 'replot' and circuit_breaker is False:
            plot_name = find_plot_to_destroy()
            circuit_breaker = can_delete_plot(plot_name)


def main():
    log_info('Create process for plotter')
#    plot_runner_process = multiprocessing.Process(target=plot_runner)
#    plot_runner_process.start()
#    plot_runner_process.join()

    if config['use_staging_directories']:
        plot_manager_process = multiprocessing.Process(target=start_copy)
        plot_manager_process.start()
        plot_manager_process.join()

    log_info("All Process done, going to exit")




if __name__ == '__main__':
    main()

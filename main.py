from harvest_disk import harvest_all_disk, calculate_plot
from replot import can_delete_plot, find_plot_to_destroy
from config import config


def main():
    circuit_breaker = True
    while circuit_breaker:
        disk_space = harvest_all_disk()
        circuit_breaker = calculate_plot(disk_space)
        if config['mode'] == 'replot':
            plot_name = find_plot_to_destroy()
            circuit_breaker = can_delete_plot(plot_name)


if __name__ == '__main__':
    main()

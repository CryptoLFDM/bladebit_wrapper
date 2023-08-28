from harvest_disk import harvest_all_disk, calculate_plot, find_plot_to_destroy
from plot import run_plot
from config import config


def main():
    circuit_breaker = True
    while circuit_breaker:
        disk_space = harvest_all_disk()
        circuit_breaker = calculate_plot(disk_space)
        if config['mode'] == 'replot':
            disk_path = find_plot_to_destroy()
            run_plot(disk_path)


if __name__ == '__main__':
    main()

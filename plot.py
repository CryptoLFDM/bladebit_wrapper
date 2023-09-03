import subprocess
from pathlib import Path
import platform
from datetime import datetime

import config_loader
from log_utils import bladebit_plotter_logger, INFO, WARNING, FAILED, SUCCESS
from utils import get_disk_info
from stagging import get_staging_plot_dir
from harvest_disk import harvest_all_disk, calculate_plot
from replot import can_delete_plot, find_plot_to_destroy


def get_nbr_plottable_max(disk_path: str) -> int:
    _, _, free = get_disk_info(disk_path)
    max_plottable = int(free / config_loader.chia_const[config_loader.config['compression_level']]['gib'])
    if max_plottable > 1:
        return max_plottable - 1
    return max_plottable


def get_binary_path() -> Path:
    if platform.system() == 'Windows':
        return Path('./binaries/bladebit_cuda.exe')
    else:
        return Path('./binaries/bladebit_cuda')


def create_plotter_argument(disk_path: str) -> list:
    plotter_args = [
        get_binary_path(),
        '-f', config_loader.config['farmer_key'],
        '-n', get_nbr_plottable_max(disk_path),
        '-c', config_loader.config['contract_key'],
        '--compress', config_loader.config['compression_level'],
        'cudaplot'
    ]
    if config_loader.config['plot_with_128GO_ram_only']:
        plotter_args = plotter_args + ['--disk-128', '-t1', Path(config_loader.config['tmp_plot_directory_for_128go_ram_support'])]
    if config_loader.config['use_staging_directories'] and get_staging_plot_dir() is not None:
        plotter_args.append(Path(get_staging_plot_dir()))
    else:
        plotter_args.append(Path(disk_path))
    return plotter_args


def run_plot(disk_path: str):
    clock_start = datetime.now()
    bladebit_plotter_logger.log(INFO, 'going to run plot with clock {}'.format(clock_start))
    try:
        cmd_string = ' '.join(map(str, create_plotter_argument(disk_path)))
        bladebit_plotter_logger.log(INFO, 'Going to run cmd `{}`'.format(cmd_string))
        with subprocess.Popen(cmd_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                              text=True) as process:
            for line in process.stdout:
                bladebit_plotter_logger.log(INFO, line.strip())

            for line in process.stderr:
                bladebit_plotter_logger.log(FAILED, line.strip())
        process.wait()
        if process.returncode == 0:
            clock_end = datetime.now()
            delta = clock_end - clock_start
            bladebit_plotter_logger.log(SUCCESS, 
                'Command executed successfully. Clock is {}, duration is {} ms'.format(clock_end, delta.seconds))
        else:
            clock_end = datetime.now()
            delta = clock_end - clock_start
            bladebit_plotter_logger.log(FAILED, 'Clock is {}, duration is {} ms. Command failed with error:'.format(clock_end, delta.seconds))
    except Exception as e:
        bladebit_plotter_logger.log(FAILED, 'An error occurred: {}'.format(e))


def plot_runner():
    path_plottable = "None"
    while path_plottable is not None:
        disk_space = harvest_all_disk()
        path_plottable = calculate_plot(disk_space)
        if path_plottable is not None:
            run_plot(path_plottable)
        if config_loader.config['mode'] == 'replot' and path_plottable is False:
            plot_name = find_plot_to_destroy()
            path_plottable = can_delete_plot(plot_name)


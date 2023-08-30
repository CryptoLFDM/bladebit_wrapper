import subprocess
from pathlib import Path
import platform
from datetime import datetime

from config import config, chia_const
from log_utils import log_info, log_failed, log_success, log_warning
from harvest_disk import get_disk_info


def get_nbr_plottable_max(disk_path: str) -> int:
    _, _, free = get_disk_info(disk_path)
    return int(free / chia_const[config['compression_level']]['gib'])


def get_binary_path() -> Path:
    if platform.system() == 'Windows':
        return Path('./binaries/bladebit_cuda.exe')
    else:
        return Path('./binaries/bladebit_cuda')


def create_plotter_argument(disk_path: str) -> list:
    plotter_args = [
        get_binary_path(),
        '-f', config['farmer_key'],
        '-n', get_nbr_plottable_max(disk_path),
        '-c', config['contract_key'],
        '--compress', config['compression_level'],
        'cudaplot'
    ]
    if config['plot_with_128GO_ram_only']:
        plotter_args = plotter_args + ['--disk-128', '-t1', Path(config['tmp_plot_directory_for_128go_ram_support'])]
    plotter_args.append(Path(disk_path))
    return plotter_args


def run_plot(disk_path: str):
    clock_start = datetime.now()
    log_info('going to run plot with clock {}'.format(clock_start))
    try:
        cmd_string = ' '.join(map(str, create_plotter_argument(disk_path)))
        log_info('Going to run cmd `{}`'.format(cmd_string))
        with subprocess.Popen(cmd_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                              text=True) as process:
            for line in process.stdout:
                log_info(line.strip())

            for line in process.stderr:
                log_failed(line.strip())
        process.wait()
        if process.returncode == 0:
            clock_end = datetime.now()
            delta = clock_end - clock_start
            log_success(
                'Command executed successfully. Clock is {}, duration is {} ms'.format(clock_end, delta.seconds))
        else:
            clock_end = datetime.now()
            delta = clock_end - clock_start
            log_failed('Clock is {}, duration is {} ms. Command failed with error:'.format(clock_end, delta.seconds))
    except Exception as e:
        log_failed('An error occurred: {}'.format(e))
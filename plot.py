import subprocess
from pathlib import Path
import platform

from config import config
from log_utils import log_info, log_failed, log_success


def get_binary_path() -> Path:
    if platform.system() == 'Windows':
        return Path('./binaries/bladebit_cuda.exe')
    else:
        return Path('./binaries/bladebit_cuda')


def create_plotter_argument(disk_path: str) -> list:
    plotter_args = [
        get_binary_path(),
        '-n', '1',
        '-f', config['farmer_key'],
        '-c', config['contract_key'],
        '--compress', str(config['compression_level']),
        'cudaplot'
    ]
    if config['plot_with_128GO_ram_only']:
        plotter_args = plotter_args + ['--disk-128', '-t1', Path(config['tmp_plot_directory_for_128go_ram_support'])]
    plotter_args.append(Path(disk_path))
    return plotter_args


def run_plot(disk_path: str):
    try:
        completed_process = subprocess.run(create_plotter_argument(disk_path), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                           shell=True)
        if completed_process.returncode == 0:
            log_success('Command executed successfully.')
            log_success(completed_process.stdout)
        else:
            log_failed('Command failed with error:')
            log_failed(completed_process.stderr)
    except Exception as e:
        log_failed('An error occurred: {}'.format(e))

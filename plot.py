import subprocess
from pathlib import Path
import platform

from config import config
from log_utils import log_info, log_failed, log_success


def run_plot(disk_path: str):
    if platform.system() == 'Windows':
        plotter_binary = Path('./binaries/bladebit_cuda.exe')
    else:
        plotter_binary = Path('./binaries/bladebit_cuda')
    plotter_args = [
        plotter_binary,
        '-n', '1',
        '-f', config['farmer_key'],
        '-c', config['contract_key'],
        '--compress', str(config['compression_level']),
        'cudaplot',
        Path(disk_path)
    ]
    log_info(plotter_args)
    try:
        completed_process = subprocess.run(plotter_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                           shell=True)
        if completed_process.returncode == 0:
            log_success("Command executed successfully.")
            log_success(completed_process.stdout)
        else:
            log_failed("Command failed with error:")
            log_failed(completed_process.stderr)
    except Exception as e:
        log_failed("An error occurred: {}".format(e))


import subprocess
from pathlib import Path
import platform

from config import config
from log_utils import log_info, log_failed, log_success


def run_plot(disk_path: str):
    # Detect OS and set plotter binary path
    if platform.system() == 'Windows':
        plotter_binary = Path('./binaries/bladebit_cuda.exe')
    else:
        plotter_binary = Path('./binaries/bladebit_cuda')

    # Define common arguments
    common_args = [
        '-n', '1',
        '-f', config['farmer_key'],
        '-c', config['contract_key'],
        '--compress', str(config['compression_level']),
    ]

    # Define optional arguments
    optional_args = []
    if "disk-128" in config and config["disk-128"] == True:
        optional_args.append("--disk-128")
        optional_args.append("-t1")
        if not "tmpdir" in config:
            raise Exception("tmpdir is not defined in config.yml")
        optional_args.append(Path(config["tmpdir"]))

    # Build final command
    plotter_args = []
    plotter_args.append(plotter_binary)
    plotter_args.extend(common_args)
    plotter_args.append("cudaplot")
    plotter_args.extend(optional_args)
    plotter_args.append(Path(disk_path))

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
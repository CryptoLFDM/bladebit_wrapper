import sys

import yaml
import pathlib
from pydantic import BaseModel, DirectoryPath, validator
from typing import List, Optional

from log_utils import bladebit_wrapper_logger, INFO, WARNING, FAILED, SUCCESS


Config = None
chia_const = None


class WrapperConfig(BaseModel):
    mode: str
    farmer_key: str
    contract_key: str
    compression_level: int
    plotter_enabled: bool
    directories_to_plot: List[DirectoryPath]
    plot_with_128GO_ram_only: bool
    tmp_plot_directory_for_128go_ram_support: Optional[DirectoryPath] = None
    use_staging_directories: bool
    staging_directories: Optional[List[DirectoryPath]] = None


def load_config(path: str):
    load_chia_const()
    config_path = pathlib.Path(path)
    try:
        with open(config_path, 'r') as yaml_file:
            try:
                global Config
                Config = WrapperConfig(**yaml.safe_load(yaml_file))
                bladebit_wrapper_logger.log(SUCCESS, 'Configuration is valid')
            except ValueError as e:
                bladebit_wrapper_logger.log(FAILED, 'Configuration is invalid: {}'.format(e))
                sys.exit(1)
    except yaml.YAMLError as e:
        bladebit_wrapper_logger.log(FAILED, 'Unable to load YAML {} caused by: {}'.format(path, e))


def load_chia_const():
    chia_const_path = pathlib.Path('config/chia.yml')
    with open(chia_const_path, 'r') as yaml_file:
        global chia_const
        chia_const = yaml.safe_load(yaml_file)

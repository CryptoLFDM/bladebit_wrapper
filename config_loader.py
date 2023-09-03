import yaml
import pathlib

config = None
chia_const = None


def load_config(path: str):
    load_chia_const()
    config_path = pathlib.Path(path)
    with open(config_path, 'r') as yaml_file:
        global config
        config = yaml.safe_load(yaml_file)


def load_chia_const():
    chia_const_path = pathlib.Path('config/chia.yml')
    with open(chia_const_path, 'r') as yaml_file:
        global chia_const
        chia_const = yaml.safe_load(yaml_file)

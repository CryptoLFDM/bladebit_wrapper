import yaml
import pathlib

config_path = pathlib.Path('config/config.yml')
with open(config_path, 'r') as yaml_file:
    config = yaml.safe_load(yaml_file)

chia_const_path = pathlib.Path('config/chia.yml')
with open(chia_const_path, 'r') as yaml_file:
    chia_const = yaml.safe_load(yaml_file)

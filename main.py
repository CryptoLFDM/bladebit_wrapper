import click

from config_loader import load_config
from orchestrator import bladebit_wrapper_orchestrator


@click.command()
@click.option('--config_file', '-c', default='config/config.yml', type=str)
def main(config_file: str):
    load_config(config_file)
    bladebit_wrapper_orchestrator()


if __name__ == '__main__':
    main()

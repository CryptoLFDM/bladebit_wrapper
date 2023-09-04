import click

from log_utils import init_logger
from config_loader import load_config
from orchestrator import bladebit_wrapper_orchestrator


@click.command()
@click.option('--config_file', '-c', default='config/config.yml', type=str, help='Use custom config')
@click.option('--debug', '-d', is_flag=True, default=False, help='Enable debug if specified')
def main(config_file: str, debug: bool):
    init_logger(debug)
    load_config(config_file)
    bladebit_wrapper_orchestrator()


if __name__ == '__main__':
    main()

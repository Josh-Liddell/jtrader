import yaml
from pathlib import Path
from .jtrader import JTrader


def main():
    # Get the path of the config file relative to this script
    config_path = Path(__file__).parent / "config.yaml"

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    jtrader = JTrader(config)
    jtrader.run()


if __name__ == "__main__":
    main()


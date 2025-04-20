#!/usr/bin/env python3
import argparse as ap
import yaml
import time


class JTrader:

    # Create the argument parser
    def __init__(self, config):
        self.parser = ap.ArgumentParser(
            description='A tool for simulating crypto arbitrage opportunities.Use it to start a background watcher that checks for arbitrage paths',
            # usage='jtrader command [options]',
            epilog='Have fun trading!',
            add_help=False,
            allow_abbrev=False)

        self._setup_parser(config)
        self.trading = False

    # Applying configuration to the parser object
    def _setup_parser(self, config):
        # Apply general argument options
        for args in config['general']:
            flags = args.pop('flags')
            self.parser.add_argument(*flags, **args)

        # Create subparsers and apply their argument options
        subparsers = self.parser.add_subparsers(dest='command', title='subcommands')
        commands = config["commands"]

        for command, data in commands.items():
            subparser = subparsers.add_parser(command, help=data["help"])
            subparser.set_defaults(func=getattr(self, data['func']))

            for args in data["args"]:
                flags = args.pop("flags")
                subparser.add_argument(*flags, **args)

    # Logic control for arugments
    def run(self):
        args = self.parser.parse_args()

        # If a subcommand was entered run its assocated function
        if args.command:
            args.func(args)
        else:
            self.parser.print_help()

    def start(self, args):
        print(f"Program started with capital: {args.capital}")
        self.trading = True

        from trading import Trader
        trader = Trader(args.capital)
        trader.trade()

        # while self.trading is True:
        # trader.trade()
        # time.sleep(60 / args.frequency)

    def stop(self, args):
        print("Program stopping")
        self.trading = False


# This code could get transfered to a main or init file later
if __name__ == '__main__':
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    jtrader = JTrader(config)
    jtrader.run()

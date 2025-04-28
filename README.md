## About
JTrader is a command-line tool for simulating triangular arbitrage to identify price discrepencies in trading paths. 
Use it to start a trading process to find and trade on these opportunities.

Trades are hapening through USDC rather than trading the currencies directly. 

## Installation
Copy and paste the commands below into the terminal
```bash
git clone https://github.com/Josh-Liddell/jtrader.git
cd jtrader
pipx install . 
```

**NOTE**
You must also:
1. Install [pipx](https://github.com/pypa/pipx)
2. Create a file in home directory called .jtrader.env that contains keys for alpaca account
```
ALPACA_API_KEY = yourkeyhere
ALPACA_SECRET_KEY = yourkeyhere
```

*Verify installation with jtrader --version*

## Usage
See jtrader --help for possible commands


## Uninstall
The tool can be uninstalled with the following command:
```bash
pipx uninstall jtrader
```

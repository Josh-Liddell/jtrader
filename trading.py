from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.trading.client import TradingClient
from alpaca.data.requests import CryptoLatestQuoteRequest
from alpaca.trading.requests import MarketOrderRequest
# from alpaca.trading.enums import OrderSide  # , TimeInForce
import networkx as nx
from itertools import permutations
from dotenv import load_dotenv
import os
from tqdm import tqdm
import time


# Jtrader class is mainly for cli tool, this class is mainly for the trading process
class Trader:

    def __init__(self, tradingcapital=1000):
        load_dotenv()
        KEY = os.getenv("ALPACA_API_KEY")
        SECRET = os.getenv("ALPACA_SECRET_KEY")

        self.capital = tradingcapital
        # self.coins = ['AAVE', 'AVAX', 'BAT', 'BCH', 'BTC', 'CRV', 'DOGE', 'DOT', 'ETH', 'GRT', 'LINK', 'LTC', 'MKR', 'SHIB', 'SUSHI', 'UNI', 'XTZ', 'YFI']
        # self.coins = ['AAVE', 'AVAX', 'BAT', 'BCH', 'BTC', 'CRV', 'DOGE', 'DOT', 'ETH', 'GRT', 'LINK']
        self.coins = ['AAVE', 'AVAX', 'BAT', 'BCH']
        self.data_client = CryptoHistoricalDataClient(KEY, SECRET)
        self.trading_client = TradingClient(KEY, SECRET, paper=True)
        self.request_crypto = CryptoLatestQuoteRequest(symbol_or_symbols=[f"{coin}/USDC" for coin in self.coins])

    def makeGraph(self):
        g = nx.DiGraph()

        # Fetching the 'coin/USDC' data from alpaca
        quotes = self.data_client.get_crypto_latest_quote(self.request_crypto)

        # For each coin permutation pair making an edge whose weight I calculate from the USDC ask prices divided by eachother
        for c1, c2 in permutations(self.coins, 2):
            bid = quotes[f"{c1}/USDC"].bid_price
            ask = quotes[f"{c2}/USDC"].ask_price
            rate = bid / ask
            g.add_edge(c1, c2, weight=rate)
            # Weight represents c1 -> USDC -> c2 exchange rate (how much c2 you get per c1 after when going through USDC)

        return g

    def find_arbitrage(self, g):
        smallwf = None
        bigwf = None

        # For each coin permutation pair we find all possible paths between them
        # And for each of those paths we multiply the edges to get path weight, and then multiply that by the corresponidng reverse path weight to get total weight fator which is around 1
        for c1, c2 in tqdm(permutations(g.nodes, 2), desc='ProcessingPaths'):
            for path in nx.all_simple_paths(g, source=c1, target=c2):
                paths = [path, list(reversed(path))]
                wf = 1
                for p in paths:
                    path_weight = 1
                    for i in range(len(p) - 1):
                        path_weight *= g[p[i]][p[i + 1]]['weight']
                    wf *= path_weight
                    # print(p, path_weight)
                # print(wf)

                if bigwf is None or wf > bigwf:
                    bigwf = wf
                    bigpaths = paths
                if smallwf is None or wf < smallwf:
                    smallwf = wf
                    smallpaths = paths

        print(f'\nSmallest Paths weight factor: {smallwf}')
        print(f'Paths: {smallpaths}')
        print(f'Greatest Paths weight factor: {bigwf}')
        print(f'Paths: {bigpaths}')

        return bigpaths[0], bigwf

    # def place_order(self, symbol, qty, side):
    #     # Prep order
    #     order = MarketOrderRequest(
    #         # time_in_force=TimeInForce.DAY
    #         symbol=symbol,
    #         qty=qty,
    #         side=OrderSide.BUY if side == "buy" else OrderSide.SELL)
    #
    #     # Submit order
    #     response = self.trading_client.submit_order(order_data=order)
    #
    #     print(f"{side.upper()} ORDER PLACED: {qty} {symbol}")

    def trade(self):

        # 1. Make a graph from latest quote data
        print("Making graph from latest quote data")
        g = self.makeGraph()

        # 2. Find the best arbitrage path
        print("Looking through all possible paths for arbitrage")
        best_path, weight_factor = self.find_arbitrage(g)

        print('\n------Now executing trades for the best path------')

        qty = self.capital  # Starting capital in USD

        print(f"\nBuying USDC with starting capital of {qty} USD...")
        order = MarketOrderRequest(
            symbol='USDC/USD',
            notional=qty,
            side='buy',
            time_in_force='gtc'
        )
        self.trading_client.submit_order(order_data=order)
        time.sleep(5)
        print('Success')

        for coin in best_path:
            # get updated USDC balance
            usdc_position = self.trading_client.get_open_position('USDCUSD')
            qty = float(usdc_position.qty_available)

            print(f"\nBuying {coin} with {qty} USDC...")
            order = MarketOrderRequest(
                symbol=f'{coin}/USDC',
                notional=qty,
                side='buy',
                time_in_force='gtc'
            )
            self.trading_client.submit_order(order_data=order)
            time.sleep(5)
            print('Success')

            # Always get updated coin balance
            coin_position = self.trading_client.get_open_position(f'{coin}USD')
            qty = float(coin_position.qty_available)

            print(f"\nSelling {coin} to get USDC...")
            order = MarketOrderRequest(
                symbol=f'{coin}/USDC',
                qty=qty,
                side='sell',
                time_in_force='gtc'
            )
            self.trading_client.submit_order(order_data=order)
            time.sleep(5)
            print('Success')

        # Final: sell USDC back to USD
        usdc_position = self.trading_client.get_open_position('USDCUSD')
        qty = float(usdc_position.qty_available)

        print(f"\nSelling USDC to get back USD with {qty} USDC...")
        order = MarketOrderRequest(
            symbol='USDC/USD',
            qty=qty,
            side='sell',
            time_in_force='gtc'
        )
        self.trading_client.submit_order(order_data=order)
        time.sleep(5)
        print('Success')

        print('Trading process complete for the best weighted path.')

        # 3. As long as best weight factor is high enough, then execute the trading process on that path using capital (buy sell buy sell buy sell)
        # if weight_factor > 1.007:
        # print("\nArbitrage found, executing trades")

        # TRADE
        # for coin in best_path:
        # self.place_order(f'{coin}/USDC', 1000, "buy")
        # Change qty
        # self.place_order(f'{coin}/USDC', 1000, "sell")
        # Change qty

        # else:
        # print("\nTrades not really worth it tbh")

    # def snapshot(self, pair):
    #     if (pair[0] in self.coins) and (pair[1] in self.coins):
    #         bigwf = None
    #         g = self.makeGraph()
    #         for path in nx.all_simple_paths(g, source=pair[0], target=pair[1]):
    #             paths = [path, list(reversed(path))]
    #             wf = 1
    #             for p in paths:
    #                 path_weight = 1
    #                 for i in range(len(p) - 1):
    #                     path_weight *= g[p[i]][p[i + 1]]['weight']
    #                 wf *= path_weight
    #
    #             if bigwf is None or wf > bigwf:
    #                 bigwf = wf
    #                 bigpaths = paths
    #
    #         print(f'Path with best weight factor: {bigpaths}')
    #         print(f'Weight factor: {bigwf}')

    def snapshot(self, pair):
        if (pair[0] in self.coins) and (pair[1] in self.coins):
            bigwf = None
            g = self.makeGraph()

            print("Building paths, this can take awhile")
            print("")
            paths_iter = list(nx.all_simple_paths(g, source=pair[0], target=pair[1]))

            for path in tqdm(paths_iter, desc="Processing paths"):
                paths = [path, list(reversed(path))]
                wf = 1
                for p in paths:
                    path_weight = 1
                    for i in range(len(p) - 1):
                        path_weight *= g[p[i]][p[i + 1]]['weight']
                    wf *= path_weight

                if bigwf is None or wf > bigwf:
                    bigwf = wf
                    bigpaths = paths

            print(f'Path with best weight factor: {bigpaths}')
            print(f'Weight factor: {bigwf}')


# NOTES
# print(g.nodes)
# for u, v, data in g.edges(data=True):
#     print(f"{u} -> {v} : {data}")

# Path looks like: BTC ETH LTC But is actually:
# 1000 USDC → BTC → USDC → ETH → USDC → LTC → USDC

# Step 1: Buy BTC with 1000 USDC
# trade_crypto("BTC/USDC", qty=1000, side="buy")  # qty in USDC

# Step 2: Wait for fill, then sell BTC for USDC
# You'd fetch BTC quantity from your account before doing this
# trade_crypto("BTC/USDC", qty=0.0158, side="sell")  # qty in BTC

# Step 3: Buy ETH with USDC
# trade_crypto("ETH/USDC", qty=980, side="buy")

# Step 4: Sell ETH for USDC
# trade_crypto("ETH/USDC", qty=0.32, side="sell")

# Step 5: Buy LTC
# trade_crypto("LTC/USDC", qty=950, side="buy")

# Step 6: Sell LTC
# trade_crypto("LTC/USDC", qty=7.8, side="sell")

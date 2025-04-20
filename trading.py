from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.trading.client import TradingClient
from alpaca.data.requests import CryptoLatestQuoteRequest
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import networkx as nx
from itertools import permutations
from dotenv import load_dotenv
import os


# Jtrader class is mainly for cli tool, this class is mainly for the trading process
class Trader:

    def __init__(self, tradingcapital):
        load_dotenv()
        KEY = os.getenv("ALPACA_API_KEY")
        SECRET = os.getenv("ALPACA_SECRET_KEY")

        self.capital = tradingcapital
        # self.coins = ['AAVE', 'AVAX', 'BAT', 'BCH', 'BTC', 'CRV', 'DOGE', 'DOT', 'ETH', 'GRT', 'LINK', 'LTC', 'MKR', 'SHIB', 'SUSHI', 'UNI', 'XTZ', 'YFI']
        self.coins = ['AAVE', 'AVAX', 'BAT', 'BCH', 'BTC', 'CRV']
        self.data_client = CryptoHistoricalDataClient(KEY, SECRET)
        self.trading_client = TradingClient(KEY, SECRET, paper=True)
        self.request_crypto = CryptoLatestQuoteRequest(symbol_or_symbols=[f"{coin}/USDC" for coin in self.coins])

    def makeGraph(self):
        g = nx.DiGraph()

        # Fetching the 'coin/USDC' data from alpaca
        quotes = self.data_client.get_crypto_latest_quote(self.request_crypto)

        # For each coin permutation pair making an edge whose weight I calculate from the USDC ask prices divided by eachother
        for c1, c2 in permutations(self.coins, 2):
            ask1, ask2 = (quotes[f"{c}/USDC"].ask_price for c in (c1, c2))
            g.add_edge(c1, c2, weight=ask1 / ask2)

        return g

    def find_arbitrage(self, g):
        smallwf = None
        bigwf = None

        # For each coin permutation pair we find all possible paths between them
        # And for each of those paths we multiply the edges to get path weight, and then multiply that by the corresponidng reverse path weight to get total weight fator which is around 1
        for c1, c2 in permutations(g.nodes, 2):
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

    def place_order(self, symbol, qty, side):
        # Prep order
        order = MarketOrderRequest(
            # time_in_force=TimeInForce.DAY
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side == "buy" else OrderSide.SELL)

        # Submit order
        response = self.trading_client.submit_order(order_data=order)

        print(f"{side.upper()} ORDER PLACED: {qty} {symbol}")

    def trade(self):

        # 1. Make a graph with latest quote data
        g = self.makeGraph()

        # 2. Check graph for arbitrage (Find path with greatest weight factor) --- This is the part that can take a little while
        best_path, weight_factor = self.find_arbitrage(g)

        # 3. As long as best weight factor is high enough, then execute the trading process on that path using capital (buy sell buy sell buy sell)
        if weight_factor > 1.007:
            print("\nArbitrage found, executing trades")

            # TRADE
            # qty = self.capital
            # for coin in best_path:
            # self.place_order(f'{coin}/USDC', 1000, "buy")
            # Change qty
            # self.place_order(f'{coin}/USDC', 1000, "sell")
            # Change qty

        else:
            print("\nTrades not really worth it tbh")


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

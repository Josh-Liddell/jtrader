from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.trading.client import TradingClient
from alpaca.data.requests import CryptoLatestQuoteRequest
import networkx as nx
from itertools import permutations
from dotenv import load_dotenv
import os


# Jtrader class is mainly for cli tool, this class is mainly for the trading process
class Trader:

    def __init__(self, tradingcapital, currencies):
        load_dotenv()
        KEY = os.getenv("ALPACA_API_KEY")
        SECRET = os.getenv("ALPACA_SECRET_KEY")

        self.capital = tradingcapital
        # self.currencies = currencies
        self.data_client = CryptoHistoricalDataClient(KEY, SECRET)
        self.trading_client = TradingClient(KEY, SECRET)
        self.request_crypto = CryptoLatestQuoteRequest(symbol_or_symbols=currencies)

    def makeGraph(self):
        g = nx.DiGraph()

        quotes = self.data_client.get_crypto_latest_quote(self.request_crypto)
        for symbol, quote in quotes.items():
            c1, c2 = symbol.split("/")
            g.add_edge(c1, c2, weight=quote.bid_price)
            g.add_edge(c2, c1, weight=(1 / quote.ask_price))

        return g

    def trade(self):
        # Trade notes:
        # make graph by retrieving quote data
        # check graph for arbitrage (find path with best weight factor?)
        # As long as best weight factor is big enough, then execute the trading process on that path using capital (buy sell buy sell buy sell)
        # Log
        # (Identify arbitrage opportuntiy by using graph with retrieved price data to find path with best weight)

        g = self.makeGraph()
        print(g.edges)
        for u, v, data in g.edges(data=True):
            print(f"{u} -> {v} : {data}")

        # Buy and sell the currencies through the path in order to profit


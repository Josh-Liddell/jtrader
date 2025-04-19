from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest

import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

client = CryptoHistoricalDataClient(API_KEY, SECRET_KEY)

# symbols = ["BTC/USD", "ETH/USD", "ETH/BTC"]
symbols = ["ETH/BTC"]
request = CryptoLatestQuoteRequest(symbol_or_symbols=symbols)
quotes = client.get_crypto_latest_quote(request)

for key, val in quotes.items():
    print(f"{key}: {val}")


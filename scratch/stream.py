from alpaca.data.live import CryptoDataStream
from dotenv import load_dotenv
import os


load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")


crypto_stream = CryptoDataStream(API_KEY, SECRET_KEY)


# Handler for live trades (best for "last price")
# @crypto_stream.subscribe_trades
async def handle_trade(trade):
    print(f"[{trade.symbol}] Last Price: {trade.price}")

# Doing this way would be alternative
crypto_stream.subscribe_trades(handle_trade, "BTC/USD")

crypto_stream.run()

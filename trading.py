from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")


# paper=True enables paper trading
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

# Try fetching account info
account = trading_client.get_account()

# Print account details
print("Account Status:", account.status)
print("Buying Power:", account.buying_power)

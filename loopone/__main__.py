from .binance import BinanceClient
from .common import get_credentials, milli_to_date
from .core import TradingEnvironment


def main():
    api_key, api_secret = get_credentials()
    worker = TradingEnvironment(api_key, api_secret)
    # worker.run_worker(worker.run_algorithm)
    x = worker.backtest()


if __name__ == "__main__":
    main()


from loopone.common import get_credentials, milli_to_date
from loopone.core import TradingEnvironment


def collect():
    api_key, api_secret = get_credentials()
    worker = TradingEnvironment(api_key, api_secret)
    worker.run_collector()


if __name__ == "__main__":
    collect()

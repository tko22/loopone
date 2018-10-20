import sys
import logging

import click
import matplotlib.pyplot as plt
from loopone.common import get_credentials, milli_to_date
from loopone.core import TradingEnvironment

DEFAULT_LOG_FILE = "loopone.log"
LOG_FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# logging
logger = logging.getLogger("loopone")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(DEFAULT_LOG_FILE)
fh.setLevel(logging.DEBUG)
fh.setFormatter(LOG_FORMATTER)

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(LOG_FORMATTER)
logger.addHandler(fh)
logger.addHandler(ch)


api_key, api_secret = get_credentials()


@click.group()
def main():
    """Our way of losing money"""
    pass


@main.command()
@click.option("-g", "--graph", is_flag=True, default=False, help="Graph Return series?")
def backtest(graph):
    """Run a backtest for the given algorithm"""
    worker = TradingEnvironment(api_key, api_secret)
    result = worker.backtest()

    click.echo(
        f"Return Series from {result['open_datetime'].iloc[-1]} to {result['close_datetime'][0]} -- {(result['return_series'][0]-1)*100 }%"
    )
    if graph:
        result.plot(x="close_datetime", y="return_series", kind="line")
        plt.gca().invert_xaxis()
        plt.show()
        plt.close()


@main.command()
def paper():
    """Run a paper trade for a given algorithm"""
    worker = TradingEnvironment(api_key, api_secret)
    worker.run_worker(worker.run_algorithm)


@main.command()
def live():
    """Trade Live"""
    pass


if __name__ == "__main__":
    main()

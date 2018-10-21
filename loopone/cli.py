import sys
import re
import logging

import click
import colorlog
import matplotlib.pyplot as plt
from .common import get_credentials, milli_to_date
from .core import TradingEnvironment

DEFAULT_LOG_FILE = "loopone.log"
DEFAULT_FORMATTER = colorlog.ColoredFormatter(
    "[%(asctime)s: %(log_color)s%(levelname)s%(reset)s]: [%(name)s]: %(log_color)s%(message)s",
    reset=True,
)

# logging
logger = logging.getLogger()  # get root logger
fh = logging.FileHandler(DEFAULT_LOG_FILE)
logger.setLevel(logging.DEBUG)
fh.setFormatter(DEFAULT_FORMATTER)

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(DEFAULT_FORMATTER)
logger.setLevel(logging.INFO)
logger.addHandler(fh)
logger.addHandler(ch)


api_key, api_secret = get_credentials()


@click.group()
def main():
    """Our way of losing money"""
    pass


@main.command()
@click.option("-g", "--graph", is_flag=True, default=False, help="Graph Return series?")
@click.option(
    "-o", "output", is_flag=True, default=False, help="Output backtest data to excel."
)
def backtest(graph, output):
    """Run a backtest for the given algorithm"""
    worker = TradingEnvironment(api_key, api_secret)
    result = worker.backtest()
    start_time = result["open_datetime"].iloc[-1]
    end_time = result["close_datetime"][0]

    click.echo(
        f"Return Series from {start_time} to {end_time} -- {(result['return_series'][0]-1)*100 }%"
    )

    if output:
        output_file_name = f"backtest-{re.sub('[ -/]+', '-', start_time)}-{re.sub('[ -/]+', '_', end_time)}.xlsx"  # regex to replace '/' and space
        result.to_excel(output_file_name)
        logger.info("Wrote result to '%s'", output_file_name)
    if graph:
        logger.info("Plotting Return Series to kline close time...")
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

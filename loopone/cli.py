import re
import runpy
import logging

import click
import colorlog
import matplotlib.pyplot as plt
from .common import get_credentials, milli_to_date
from .core import TradingEnvironment

api_key, api_secret = get_credentials()
logger = logging.getLogger(__name__)


@click.group()
def main():
    """Our way of losing money"""
    pass


@main.command()
@click.option("-g", "--graph", is_flag=True, default=False, help="Graph Return series?")
@click.option(
    "-o", "output", is_flag=True, default=False, help="Output backtest data to excel."
)
@click.option("-f", "--file", help="path to file with algorithm")
def backtest(graph, output, file):
    """Run a backtest for the given algorithm"""
    # imported_file = runpy.run_path(file)
    # handle_data_func = imported_file.get("handle_data")

    # if not handle_data_func:
    #     click.echo(
    #         f"{file} doesn't have handle_data function. Please check if you have it."
    #     )
    #     return

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
@click.option("-f", "--file", help="path to file with trading algorithm")
def paper(file):
    """Run a paper trade for a given algorithm"""
    imported_file = runpy.run_path(file)
    handle_data_func = imported_file.get("handle_data")

    if not handle_data_func:
        click.echo(
            f"{file} doesn't have handle_data function. Please check if you have it."
        )
        return
    worker = TradingEnvironment(api_key, api_secret)
    worker.run_worker(worker.run_algorithm)


@main.command()
@click.option("-s", "--sessionID", required=True, help="paper trading session id")
def get_paper_stats(sessionID: str):
    """Get Paper trading session Statistics"""
    # query mongodb for trading sessionID
    pass


@main.command()
def live():
    """Trade Live"""
    pass


if __name__ == "__main__":
    main()

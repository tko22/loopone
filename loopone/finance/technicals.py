"""Helper functions for technicals such as SMA"""
import pandas as pd
from typing import Union, List


def get_volume():
    pass


def get_sma(data: pd.Series, num_of_periods: int) -> float:
    """Returns simple moving average given a Series of floats (can be in str).
    
    Note: Remember to not pass in the current kline
    """

    if len(data) < num_of_periods:
        return None
    data = data[:num_of_periods]
    data = data.astype(float)
    return data.mean()


def generate_sma_list(data: pd.Series, duration: int = 20) -> pd.Series:
    """Generate a list of SMA given a Series of prices."""
    if len(data) < duration:
        return None
    new_data = data.astype(float)

    return pd.DataFrame(
        [new_data[x : x + duration].mean() for x in range(0, len(new_data) - duration)]
    )


def generate_ema_list(
    closing_prices: pd.Series, sma_list: pd.Series, duration: int = 10
) -> pd.Series:
    """Returns Exponential Moving Average List given pandas series of Closing Prices."""
    # first exponential moving average reference point is simple
    # '1000' proxy for our furthest back available data
    # ema = ((current price - previous EMA) * weight) + previous EMA
    weight = 2 / (duration + 1)
    ret = []
    if sma_list is None:
        sma_list = generate_sma_list(closing_prices, duration)
    last_valid_sma_idx = sma_list.last_valid_index()

    oldest_sma = sma_list[last_valid_sma_idx]  # given most-current on top

    oldest_ema = (
        (closing_prices[len(closing_prices) - duration] - oldest_sma) * weight
    ) + oldest_sma
    ret.append(oldest_ema)

    for index in range(1, len(closing_prices) - duration + 1):

        ret.insert(
            0,
            (closing_prices[len(closing_prices) - duration - index] - ret[0]) * weight
            + ret[0],
        )
    return pd.Series(ret)


def get_percent_change(input: pd.Series) -> pd.Series:
    """
    Generate percent changes per minute

    :params panda Series of close prices
    :returns panda Series of percent changes
    """
    ret = []
    # go until the 2nd to last moment because it should be 1 at the end of the list
    for i in range(0, len(input) - 1):
        # divide current price divided by the previous price minus one
        # insert to front of list
        ret.append(input[i] / input[i + 1] - 1)
    ret.append(1)  # add 1 to the end of list

    return pd.Series(ret)


def get_bid_ask_spread(bid: float, ask: float) -> float:
    return ask - bid

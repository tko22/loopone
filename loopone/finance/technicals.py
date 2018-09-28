"""Helper functions for technicals such as SMA"""
import pandas as pd
from typing import Union


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


def generate_sma_list(data: pd.Series, duration: int) -> pd.Series:
    """Generate a list of SMA given a Series of prices."""
    if len(data) < duration:
        return None
    data = data.astype(float)

    return pd.DataFrame(
        [data[x : x + duration].mean() for x in range(0, len(data) - duration)]
    )


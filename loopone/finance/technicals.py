"""Helper functions for technicals such as SMA"""
import pandas as pd
from typing import Union


def get_volume():
    pass


def get_twenty_hr_moving_avg(data: pd.Series) -> float:
    """Returns twenty hour moving average given a Series of floats (can be in str)."""

    if len(data) < 20:
        return None
    data = data[len(data) - 21 : -1]
    data = data.astype(float)
    return data.mean()


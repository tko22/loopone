from typing import Dict

import pandas as pd

from loopone.common import milli_to_date
from loopone.finance.technicals import get_sma


class DataTopic(object):
    __slots__ = [
        "symbol",
        "price",
        "event_time",
        "kline_start_time",
        "kline_close_time",
        "interval",
        "first_trade_id",
        "last_trade_id",
        "open_price",
        "close_price",
        "high_price",
        "low_price",
        "base_asset_volume",
        "num_of_trades",
        "kline_closed",
        "quote_asset_volume",
        "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume",
        "history",
    ]

    def __init__(self, data: Dict, history: pd.DataFrame, sma: float = None) -> None:

        kline_data = data["k"]

        self.symbol = data["s"]
        self.price = kline_data["c"]
        self.event_time = milli_to_date(data["E"])
        self.kline_start_time = milli_to_date(kline_data["t"])
        self.kline_close_time = milli_to_date(kline_data["T"])
        self.interval = kline_data["i"]
        self.first_trade_id = kline_data["f"]
        self.last_trade_id = kline_data["L"]
        self.open_price = float(kline_data["o"])
        self.close_price = float(kline_data["c"])
        self.high_price = float(kline_data["h"])
        self.low_price = float(kline_data["l"])
        self.base_asset_volume = float(kline_data["v"])
        self.num_of_trades = kline_data["n"]
        self.kline_closed = kline_data["x"]
        self.quote_asset_volume = kline_data["q"]
        self.taker_buy_base_asset_volume = kline_data["V"]
        self.taker_buy_quote_asset_volume = kline_data["Q"]
        self.history = history

    # def volume(self):
    #     pass

    # def history(self):
    #     pass

    # def current(self):
    #     pass

    def get_twenty_sma(self) -> float:
        data = pd.Series(self.history["close_price"])
        return get_sma(data, 20)

    def get_ema(self):
        pass

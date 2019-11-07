import logging
from typing import Dict

import pandas as pd

from loopone.common import milli_to_date
from loopone.finance.technicals import get_sma, get_bid_ask_spread

logger = logging.getLogger(__name__)


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
        "slot",
    ]

    def __init__(self, data: Dict, history: pd.DataFrame, book: Dict) -> None:

        kline_data: Dict = data["k"]

        self.symbol: str = data["s"]
        self.price: float = float(kline_data["c"])  # same as close price
        self.event_time = milli_to_date(data["E"])
        self.kline_start_time = milli_to_date(kline_data["t"])
        self.kline_close_time = milli_to_date(kline_data["T"])
        self.interval = kline_data["i"]
        self.first_trade_id = kline_data["f"]
        self.last_trade_id = kline_data["L"]
        self.open_price: float = float(kline_data["o"])
        self.close_price: float = float(kline_data["c"])
        self.high_price: float = float(kline_data["h"])
        self.low_price: float = float(kline_data["l"])
        self.base_asset_volume: float = float(kline_data["v"])
        self.num_of_trades = kline_data["n"]
        self.kline_closed = kline_data["x"]
        self.quote_asset_volume: float = float(kline_data["q"])
        self.taker_buy_base_asset_volume = kline_data["V"]
        self.taker_buy_quote_asset_volume = kline_data["Q"]
        self.spread = None
        self.history = history

        if self.symbol.upper() == book["symbol"]:
            self.spread = get_bid_ask_spread(book["bidPrice"], book["askPrice"])
        else:
            logger.warning("Datatopic symbol: %s doesn't match with book ")

    def __new__(cls, data: Dict, history: pd.DataFrame, book: Dict):
        import ipdb

        ipdb.set_trace()
        if data["s"].upper() == book["symbol"]:
            return super(DataTopic, cls).__new__(cls)
        else:
            raise ValueError

    # def volume(self):
    #     pass

    # def history(self):
    #     pass

    # def current(self):
    #     pass
    def __getitem__(self, idx) -> pd.Series:
        """Returns row `idx` of the historic data"""
        return self.history.iloc[idx]

    def twenty_sma(self, index: int = 0) -> float:
        return self.history["sma_history"][index]

    def ema(self, index: int = 0) -> float:
        return self.history["ema_history"][index]

    def curr_percent_change(self) -> float:
        return (self.close_price / self.history["close_price"][0]) - 1

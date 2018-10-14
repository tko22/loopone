import json
import time
from typing import Dict

import pandas as pd
from common import KlineDataSchema
from data_topic import DataTopic
from finance.technicals import get_sma, generate_sma_list, generate_ema_list
from binance_enums import KlineIntervals


# TODO Make requests for additional information asynchrounous, adding them into a list of tasks


class DataPortal(object):
    def __init__(
        self, client, symbol: str, collect: bool = False, num_of_periods: int = 20
    ):
        self.symbol = symbol
        self.client = client
        self.stream = client.get_ws_price_stream(
            symbol, interval=KlineIntervals.ONE_MIN.value
        )
        self.collect = collect  # change this to trading type later
        self.num_of_periods = num_of_periods

    async def data_stream(self) -> Dict:
        # TODO make this return a DataTopic instead
        history: pd.DataFrame() = None
        curr_start_time: str = None
        async for msg in self.stream:
            data = json.loads(msg.data)["data"]

            kline_data = data["k"]
            if curr_start_time != kline_data["t"]:
                print("getting new moving avg")
                curr_start_time = kline_data["t"]
                historic_data = self.client.get_kline(self.symbol, limit=50)
                reverse_historic_data = list(
                    reversed(historic_data)
                )  # most current on the top
                history = pd.DataFrame(
                    reverse_historic_data[
                        :-1
                    ],  # don't include the last elm (current ongoing kline)
                    columns=[
                        "open_time",
                        "open_price",
                        "high_price",
                        "low_price",
                        "close_price",
                        "volume",
                        "close_time",
                        "quote_asset_volume",
                        "num_of_trades",
                        "taker_buy_base_asset_volume",
                        "taker_buy_quote_asset_volume",
                        "ignore",
                    ],
                    dtype="float64",
                )
                # history["close_price"] = history["close_price"].astype(float)
                history["sma_history"] = generate_sma_list(history["close_price"], 20)
                history["ema_history"] = generate_ema_list(
                    history["close_price"], history["sma_history"], 20
                )
                
            dt = DataTopic(data=data, history=history)

            yield dt


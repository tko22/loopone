import json
import logging
from typing import Dict

import pandas as pd

from loopone.common import KlineDataSchema, milli_to_str, kline_bn_to_df
from loopone.data_topic import DataTopic
from loopone.finance.technicals import (
    get_sma,
    generate_sma_list,
    generate_ema_list,
    get_percent_change,
)
from loopone.enums import KlineIntervals
from loopone.gateways.binance import BinanceClient

logger = logging.getLogger(__name__)
# TODO Make requests for additional information asynchrounous, adding them into a list of tasks


class DataPortal(object):
    def __init__(
        self,
        client: BinanceClient,
        symbol: str,
        collect: bool = False,
        num_of_periods: int = 20,
    ):
        self.symbol = symbol
        self.client = client
        self.stream = client.get_ws_price_stream(
            symbol, interval=KlineIntervals.ONE_MIN
        )
        self.collect = collect  # change this to trading type later
        self.num_of_periods = num_of_periods

    async def data_stream(self) -> DataTopic:
        history: pd.DataFrame() = None
        curr_start_time: int = 0
        book = await self.client.get_book_ticker(self.symbol)
        async for msg in self.stream:
            data = json.loads(msg.data)["data"]

            # update book every 3 seconds, updates when kline changes as well - look below
            if curr_start_time % 3 == 0:
                book = await self.client.get_book_ticker(self.symbol)

            kline_data = data["k"]

            # new kline entry - based on interval. Stream
            if curr_start_time != kline_data["t"]:
                # TODO instead of replacing history and recalculating everything, we can just add the new kline

                logger.info(
                    "Getting new moving avg and adding new kline entry to history..."
                )
                book = await self.client.get_book_ticker(
                    self.symbol
                )  # overwrite book that was set

                curr_start_time = kline_data["t"]
                historic_data = self.client.get_kline(
                    self.symbol, interval=KlineIntervals.ONE_MIN, limit=100
                )
                reverse_historic_data = list(
                    reversed(historic_data)
                )  # most current on the top
                history = kline_bn_to_df(
                    reverse_historic_data[:-1]
                )  # don't include the last elm (current ongoing kline))

                history["sma_history"] = generate_sma_list(history["close_price"], 20)
                history["ema_history"] = generate_ema_list(
                    history["close_price"], history["sma_history"], 10
                )
                history["percent_change"] = get_percent_change(history["close_price"])
                history["open_datetime"] = history.apply(
                    lambda row: milli_to_str(row["open_time"]), axis=1
                )
                history["close_datetime"] = history.apply(
                    lambda row: milli_to_str(row["close_time"]), axis=1
                )

            # initialize the datatopic object for the next streamed price data
            dt = DataTopic(data=data, history=history, book=book)  # Note: history

            yield dt


import asyncio
import time

import pandas as pd
from enums import TradingType, State, OrderType, KlineIntervals
from binance import BinanceClient
from data_portal import DataPortal
from common import milli_to_date, kline_bn_to_df, milli_to_str
from finance.technicals import (
    get_sma,
    generate_ema_list,
    generate_sma_list,
    get_percent_change,
)
from models import KlineRecord


class TradingEnvironment(object):
    """
    Trading Environment. This integrates everything together, from the data streams to the algorithms 
    while managing the application state. Algorithms will be using this API.
    """

    # TODO allow api_key and secret and binance client setup to be optional
    def __init__(
        self, api_key: str, api_secret: str, trading_type: str = TradingType.PAPER.name
    ) -> None:
        self.trading_type: str = trading_type
        self.state = State.STANDBY  # enum
        self.__api_key: str = api_key
        self.__api_secret: str = api_secret
        self.loop: asyncio.AbstractEventLoop = (
            asyncio.get_event_loop()
        )  # TODO make it an event loop in which we plug the binance client in
        self._client = BinanceClient(api_key, api_secret, self.loop)

    async def run_algorithm(self):
        dp = DataPortal(self._client, "ethbtc")
        ctx = {}

        async for dt in dp.data_stream():
            print("Close Price:", dt.price)
            print("open", dt.kline_start_time)
            print("\n")
            # run algo

    def backtest(self):
        raw_data = self._client.get_historical_klines(
            "ethbtc"
        )  # defaults to 5000 1m klines
        klines = kline_bn_to_df(list(reversed(raw_data)))

        klines["Open Datetime"] = klines.apply(
            lambda row: milli_to_str(row["open_time"]), axis=1
        )
        klines["Closed Datetime"] = klines.apply(
            lambda row: milli_to_str(row["close_time"]), axis=1
        )
        klines["sma_history"] = generate_sma_list(klines["close_price"], 20)
        klines["ema_history"] = generate_ema_list(
            klines["close_price"], klines["sma_history"], 10
        )
        klines["percent_change"] = get_percent_change(klines["close_price"])

        # ------------------------------------------#
        # ALGO
        trade_signal = []
        # long (1) if EMA > SMA
        # short (0) if SMA > EMA
        for x in range(0, len(klines["close_price"])):
            # TODO find a way to inject the algo here, need to create a data portal for it
            if klines["ema_history"][x] > klines["sma_history"][x]:
                trade_signal.append(1)
            else:
                trade_signal.append(0)

        return_list = [1] * klines["close_price"].count()
        # FIND RETURN SERIES
        for x in range(len(klines["close_price"]) - 2, -1, -1):

            if trade_signal[x] == 0:
                return_list[x] = return_list[x + 1]
            else:
                # buy trade signal
                return_list[x] = return_list[x + 1] * (1 + klines["percent_change"][x])
        klines["trade_signal"] = trade_signal
        klines["return_series"] = return_list

        return klines

    def run_worker(self, func):
        try:
            self.loop.run_until_complete(func())
        except KeyboardInterrupt:
            print("Interrupted")
        finally:
            self.stop()

    async def get_environment(self):
        pass

    async def schedule_function(self):
        pass

    # ---------------------------------------------------- #
    # The following functions are api functions for the algorithm

    async def order(self, type: OrderType):
        """Make an Order"""
        pass

    async def symbol_price(self, symbol_price: str):
        pass

    async def set_stop_loss(self):
        pass

    async def symbol_volume(self):
        pass

    async def account(self):
        pass

    def stop(self):
        print("Stopping....")
        self.loop.run_until_complete(self._client.close_session())
        self.loop.stop()
        self.loop.close()

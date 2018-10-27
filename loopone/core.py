import asyncio
import logging
from datetime import datetime

import pandas as pd
from .enums import TradingType, State, OrderType, KlineIntervals, OrderSide
from .binance import BinanceClient
from .data_portal import DataPortal
from .data_topic import DataTopic
from .common import milli_to_date, kline_bn_to_df, milli_to_str, connect_to_mongo
from .finance.technicals import (
    get_sma,
    generate_ema_list,
    generate_sma_list,
    get_percent_change,
)
from .models import KlineRecord, PaperTradeOrder


class TradingEnvironment(object):
    """
    Trading Environment. This integrates everything together, from the data streams to the algorithms 
    while managing the application state. Algorithms will be using this API.
    """

    # TODO allow api_key and secret and binance client setup to be optional
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        trading_type: str = TradingType.PAPER.name,
        verbose: bool = False,
    ) -> None:
        self.trading_type: str = trading_type
        self.state = State.STANDBY  # enum
        self.verbose: bool = verbose
        self.__api_key: str = api_key
        self.__api_secret: str = api_secret
        self.loop: asyncio.AbstractEventLoop = (
            asyncio.get_event_loop()
        )  # TODO make it an event loop in which we plug the binance client in
        self._client = BinanceClient(api_key, api_secret, self.loop)
        self.logger = logging.getLogger(__name__)
        connect_to_mongo()

    async def run_algorithm(self):
        dp = DataPortal(self._client, "ethbtc")
        ctx = {}
        curr_st: int = None  # current kline start time
        async for dt in dp.data_stream():
            if self.verbose:
                self.logger.info(
                    "New Data... %s at %s with volume %s",
                    dt.symbol,
                    dt.price,
                    dt.base_asset_volume,
                )
            if not curr_st:
                # handle initial
                curr_st = dt.kline_start_time
            # compares datetime
            elif curr_st != dt.kline_start_time:
                self.logger.info("New kline.... Getting trade signal")
                # new kline interval. Run algo for trade signal and make trade.
                curr_st = dt.kline_start_time
                # compare current price with the previous kline
                # need to compare the 2nd kline because the newly
                # added kline is the one that just ended
                self.logger.info("ema: %s.. sma: %s", dt.ema(1), dt.twenty_sma(1))
                import ipdb

                ipdb.set_trace()
                if dt.ema(1) > dt.twenty_sma(1):
                    await self.order(dt, OrderSide.SIDE_BUY)
                else:
                    await self.order(dt, OrderSide.SIDE_SELL)

    def backtest(self):
        self.logger.info("Starting backtest...")
        raw_data = self._client.get_historical_klines(
            "ethbtc"
        )  # defaults to 5000 1m klines
        klines = kline_bn_to_df(list(reversed(raw_data)))

        klines["open_datetime"] = klines.apply(
            lambda row: milli_to_str(row["open_time"]), axis=1
        )
        klines["close_datetime"] = klines.apply(
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
        self.stop()
        return klines

    def run_worker(self, func):
        try:
            self.loop.run_until_complete(func())
        except KeyboardInterrupt:
            self.logger.info("Keyboard Interrupted")
        finally:
            self.stop()

    async def get_environment(self):
        pass

    async def schedule_function(self):
        pass

    def set_verbose(self, val):
        self.logger.info("Setting verbosity from %s to %s", self.verbose, val)
        self.verbose = val

    def set_state(self):
        pass

    def stop(self):
        self.logger.info("Stopping Trading Environment and async loop... Goodbye")
        self.loop.run_until_complete(self._client.close_session())
        self.loop.stop()
        self.loop.close()

    # ---------------------------------------------------- #
    # The following functions are api functions for the algorithm

    async def order(
        self, dt: DataTopic, order_side: OrderSide, type: OrderType = OrderType.MARKET
    ) -> bool:
        """Make an Order"""
        # TODO check if it's live or paper trading
        self.logger.info(
            "%s %s at price: %s",
            "Buying" if order_side == OrderSide.SIDE_BUY else "Selling",
            dt.symbol,
            dt.price,
        )

        new_order = PaperTradeOrder(
            symbol=dt.symbol,
            time_executed=datetime.now(),
            quantity=0.3,
            market_volume=dt.quote_asset_volume,
            price=dt.price,
            order_side=order_side.value,
        )
        new_order.save()
        return True

    async def symbol_price(self, symbol_price: str):
        pass

    async def set_stop_loss(self):
        pass

    async def symbol_volume(self):
        pass

    async def account(self):
        pass

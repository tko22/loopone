import asyncio
import time

import pandas as pd
from enums import TradingType, State, OrderType
from binance import BinanceClient
from data_portal import DataPortal
from common import milli_to_date
from models import KlineRecord
from finance.technicals import get_sma


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

        # streaming data
        async for dt in dp.data_stream():
            if dt.base_asset_volume > 100:
                print("hi")
            
            import ipdb; ipdb.set_trace()
            print("Close Price:", dt.price)
            # print("open", dt.kline_start_time)
            print("\n")

    async def collect(self):
        ws = self._client.get_ws_price_stream("ethbtc")
        dp = DataPortal(ws, "hoteth")
        curr_start_time: str = None
        moving_avg: float = None
        async for msg in dp.data_stream():
            data = msg["data"]
            kline_data = data["k"]

            if curr_start_time != kline_data["t"]:
                curr_start_time = kline_data["t"]
                print("getting new moving avg")
                history_data = self._client.get_kline("ethbtc", limit=50)
                pd_data = pd.DataFrame(history_data)
                pd_data = pd.Series(pd_data[4])
                moving_avg = get_sma(pd_data, 20)

            record = KlineRecord(
                symbol=data["s"],
                price=kline_data["c"],
                event_time=milli_to_date(data["E"]),
                kline_start_time=milli_to_date(kline_data["t"]),
                kline_close_time=milli_to_date(kline_data["T"]),
                interval=kline_data["i"],
                first_trade_id=kline_data["f"],
                last_trade_id=kline_data["L"],
                open_price=float(kline_data["o"]),
                close_price=float(kline_data["c"]),
                high_price=float(kline_data["h"]),
                low_price=float(kline_data["l"]),
                base_asset_volume=float(kline_data["v"]),
                num_of_trades=kline_data["n"],
                kline_closed=kline_data["x"],
                quote_asset_volume=kline_data["q"],
                taker_buy_base_asset_volume=kline_data["V"],
                taker_buy_quote_asset_volume=kline_data["Q"],
                twenty_hour_moving_average=moving_avg,
            )
            record.save()
            print("adding record")

    def run_collector(self):
        try:
            self.loop.run_until_complete(self.collect())
        except KeyboardInterrupt:
            print("Interrupted")
        finally:
            self.stop()

    def run_worker(self):
        try:
            self.loop.run_until_complete(self.run_algorithm())
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

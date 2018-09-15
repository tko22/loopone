import asyncio
import time

from enums import TradingType, State
from binance import BinanceClient
from data_portal import DataPortal


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

    async def order(self):
        """Make an Order"""
        pass

    async def run_algorithm(self):
        initial_time = time.time()
        ws = self._client.get_ws_price_stream("ethbtc")
        dp = DataPortal(ws, "ethbtc")
        ctx = {}
        async for msg in dp.data_stream():
            print(msg)
            if time.time() - initial_time >= 10:
                break
        print("loop down")

    def run_worker(self):
        try:
            self.loop.run_until_complete(self.run_algorithm())
        except KeyboardInterrupt:
            print("Interrupted")
        finally:
            print("finally")
            self.stop()

    async def get_environment(self):
        pass

    async def schedule_function(self):
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
        self.loop.run_until_complete(self._client.close_session())
        print("stop")
        self.loop.stop()
        self.loop.close()

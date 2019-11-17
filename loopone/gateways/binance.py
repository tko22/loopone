import hashlib
import hmac
import time
import asyncio
import logging
from typing import Dict, Callable
from datetime import datetime

import requests
import aiohttp

from loopone.common import convert_dict_to_request_body, interval_to_milli
from loopone.enums import State, TradingType, KlineIntervals
from loopone.exceptions import BinanceRegAPIException, BinanceAsyncAPIException

API_URL = "https://api.binance.com/api"
STREAM_URL = "wss://stream.binance.com:9443/"
REQ_RATE_VIOLATION_CODE = 429
REQ_BAN_CODE = 418
DEFAULT_TIMEOUT = 10
PUBLIC_API_VERSION = "v1"
PRIVATE_API_VERSION = "v3"

logger = logging.getLogger(__name__)


def toggle_real_mode(func: Callable):
    def wrapper(self, *args, **kwargs):
        print(
            "I am the decorator, I know that self is",
            self.real_trade,
            "and I can do whatever I want with it!",
        )
        print("I also got other args:", args, kwargs)
        func(self)

    return wrapper


class BinanceClient(object):
    def __init__(
        self, api_key: str, api_secret: str, loop: asyncio.AbstractEventLoop = None
    ) -> None:
        self.__api_key: str = api_key
        self.__api_secret: str = api_secret
        self.loop: asyncio.AbstractEventLoop = loop
        if loop:
            self.async_session = aiohttp.ClientSession(loop=loop)
        self.session = self._init_session(api_key, api_secret)

    def _init_session(self, api_key: str, api_secret: str) -> requests.Session:
        session = requests.Session()
        session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "binance/python",
                "X-MBX-APIKEY": api_key,
            }
        )
        return session

    async def close_session(self):
        logger.info("Closing binance client session...")
        await self.async_session.close()

    def _generate_signature(
        self, query_string: str = None, payload: Dict = None
    ) -> str:

        # default string
        concat_string = ""
        if query_string:
            concat_string = query_string

        if payload:
            # concatenate query string with request body (that has & around each key-value pair)
            concat_string += convert_dict_to_request_body(payload)

        m = hmac.new(
            self.__api_secret.encode("utf-8"),
            concat_string.encode("utf-8"),
            hashlib.sha256,
        )
        return m.hexdigest()

    def _handle_response(self, response: requests.Response) -> Dict:
        if response.status_code != requests.codes.ok:
            if (
                response.status_code == REQ_RATE_VIOLATION_CODE
                or response.status_code == REQ_BAN_CODE
            ):
                self.change_state(State.STANDBY.name)

            raise BinanceRegAPIException(response)
        return response.json()

    async def _async_handle_response(self, response: requests.Response) -> Dict:
        if response.status != requests.codes.ok:
            if (
                response.status == REQ_RATE_VIOLATION_CODE
                or response.status == REQ_BAN_CODE
            ):
                self.change_state(State.STANDBY.name)

            try:
                json_res = await response.json()
            except ValueError:
                raise BinanceAsyncAPIException(
                    response,
                    None,
                    f"Invalid JSON error message from Binance: {response.text}",
                )
            else:
                raise BinanceAsyncAPIException(response, json_res, json_res["msg"])
        return await response.json()

    def _request(self, method: str, uri: str, signed: bool = True, **kwargs) -> Dict:
        # We don't use query strings, opting to always passing parameters through the request body
        new_kwargs = kwargs
        # set default requests timeout
        new_kwargs["timeout"] = DEFAULT_TIMEOUT

        if signed:
            if not new_kwargs.get("data"):
                new_kwargs["data"] = {}
            new_kwargs["data"]["timestamp"] = int(time.time() * 1000)
            new_kwargs["data"]["signature"] = self._generate_signature(
                payload=kwargs["data"]
            )

        response = getattr(self.session, method)(uri, **new_kwargs)
        return self._handle_response(response)

    async def _async_request(
        self, method: str, uri: str, signed: bool = True, **kwargs
    ) -> Dict:
        # We don't use query strings, opting to always passing parameters through the request body
        new_kwargs = kwargs
        # set default requests timeout
        new_kwargs["timeout"] = DEFAULT_TIMEOUT

        if signed:
            if not new_kwargs.get("data"):
                new_kwargs["data"] = {}
            new_kwargs["data"]["timestamp"] = int(time.time() * 1000)
            new_kwargs["data"]["signature"] = self._generate_signature(
                payload=kwargs["data"]
            )
        response = await getattr(self.async_session, method)(uri, **new_kwargs)

        return await self._async_handle_response(response)

    def _create_api_uri(
        self, path, version: str = PUBLIC_API_VERSION, signed: bool = False
    ) -> str:
        v = PRIVATE_API_VERSION if signed else version
        return f"{API_URL}/{v}/{path}"

    def _request_api(
        self, method: str, path: str, version: str, signed: bool, **kwargs
    ):
        uri = self._create_api_uri(path, version, signed)
        return self._request(method, uri, signed, **kwargs)

    async def _async_get(
        self,
        path: str,
        version: str = PUBLIC_API_VERSION,
        signed: bool = False,
        **kwargs,
    ) -> Dict:
        uri = self._create_api_uri(path, version, signed)
        return await self._async_request("get", uri, signed, **kwargs)

    def _get(
        self,
        path: str,
        version: str = PUBLIC_API_VERSION,
        signed: bool = False,
        **kwargs,
    ) -> Dict:
        return self._request_api("get", path, version, signed, **kwargs)

    def _post(
        self,
        path: str,
        version: str = PUBLIC_API_VERSION,
        signed: bool = False,
        **kwargs,
    ) -> Dict:
        return self._request_api("post", path, version, signed, **kwargs)

    def _put(
        self,
        path: str,
        version: str = PUBLIC_API_VERSION,
        signed: bool = False,
        **kwargs,
    ) -> Dict:
        return self._request_api("put", path, version, signed, **kwargs)

    def _delete(
        self,
        path: str,
        version: str = PUBLIC_API_VERSION,
        signed: bool = False,
        **kwargs,
    ) -> Dict:
        return self._request_api("delete", path, version, signed, **kwargs)

    ##################
    #  api wrappers  #
    ##################

    async def get_ticker_price(self, symbol: str) -> Dict:
        """Get Price of Asset (symbol = ETHBTC)

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#symbol-price-ticker
        """
        return await self._async_get("ticker/price", params={"symbol": symbol.upper()})

    def get_ticker_24hr_change(self, symbol: str) -> Dict:
        """Get 24hr change given a symbol

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#24hr-ticker-price-change-statistics
        """
        return self._get("24hr", params={"symbol": symbol.upper()})

    def get_kline(
        self,
        symbol: str,
        interval: KlineIntervals = KlineIntervals.ONE_MIN,
        start_time: int = None,
        end_time: int = None,
        limit: int = 500,
    ) -> Dict:
        """Get's Kline given a symbol with a 1w interval
        
        Link to API Docs: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#klinecandlestick-data
        """
        return self._get(
            "klines",
            params={
                "symbol": symbol.upper(),
                "interval": interval.value,
                "startTime": start_time,
                "endTime": end_time,
                "limit": limit,
            },
        )

    async def get_book_ticker(self, symbol: str) -> Dict:
        """Get Best price/qty on the order book for a symbol or symbols.

        Link to API Docs: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#symbol-order-book-ticker
        """
        return await self._async_get(
            "ticker/bookTicker",
            version=PRIVATE_API_VERSION,
            params={"symbol": symbol.upper()},
        )

    ############
    # streams #
    ###########

    async def get_ws_price_stream(
        self, symbol: str, interval: KlineIntervals = KlineIntervals.ONE_MIN
    ) -> aiohttp.ClientWebSocketResponse:
        """Yields websocket Kline stream and closes it at the end

        Link to API Docs: https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#klinecandlestick-streams

        Each Payload:
        {
            "e": "kline",     // Event type
            "E": 123456789,   // Event time
            "s": "BNBBTC",    // Symbol
            "k": {
                "t": 123400000, // Kline start time
                "T": 123460000, // Kline close time
                "s": "BNBBTC",  // Symbol
                "i": "1m",      // Interval
                "f": 100,       // First trade ID
                "L": 200,       // Last trade ID
                "o": "0.0010",  // Open price
                "c": "0.0020",  // Close price
                "h": "0.0025",  // High price
                "l": "0.0015",  // Low price
                "v": "1000",    // Base asset volume
                "n": 100,       // Number of trades
                "x": false,     // Is this kline closed?
                "q": "1.0000",  // Quote asset volume
                "V": "500",     // Taker buy base asset volume
                "Q": "0.500",   // Taker buy quote asset volume
                "B": "123456"   // Ignore
            }
        }

        :param symbol
        :param interval 
        """
        lower_symbol = symbol.lower()
        logger.info(
            "Starting up WS stream for %s at interval %s", lower_symbol, interval.value
        )
        async with self.async_session.ws_connect(
            f"{STREAM_URL}stream?streams={lower_symbol}@kline_{interval.value}"
        ) as ws:
            async for msg in ws:
                yield msg
        await self.async_session.close()

    ######################
    #  account endpoints #
    ######################

    def create_order(
        self, symbol: str, side: str, type: str, quantity: float, **params
    ):
        """Send in a new order
        Any order with an icebergQty MUST have timeInForce set to GTC.
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#new-order--trade
        :param symbol: required
        :type symbol: str
        :param side: required
        :type side: str
        :param type: required
        :type type: str
        :param timeInForce: required if limit order
        :type timeInForce: str
        :param quantity: required
        :type quantity: decimal
        :param price: required
        :type price: str
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param icebergQty: Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
        :type icebergQty: decimal
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int
        :returns: API response
        
        """
        return self._post("order", True, data=params)

    def get_historical_klines(
        self,
        symbol: str,
        interval: KlineIntervals = KlineIntervals.ONE_MIN,
        rounds: int = 5,
    ):
        """Get Historical Klines from Binance based on 1000 kline rounds
        If 5 rounds was given, 5000 klines will be given
        
        """
        limit = 1000
        logger.info("Getting %d Historical Klines from binance...", limit * rounds)
        # init our list
        output_data = []

        # convert interval to useful value in seconds
        timeframe = interval_to_milli(interval.value) * limit

        prev_data = self.get_kline(symbol, interval=interval, limit=limit)
        output_data += prev_data

        # go from 1 -> rounds - 1
        for idx in range(1, rounds):
            # fetch the klines from start_ts up to max 500 entries or the end_ts if set
            temp = self.get_kline(
                symbol=symbol,
                interval=interval,
                start_time=prev_data[0][0] - timeframe * idx,
                end_time=prev_data[0][6] - 60 * 1000,
                limit=limit,
            )
            # handle the case where exactly the limit amount of data was returned last loop
            if not len(temp):
                break
            # append this loops data to our output data
            output_data = temp + output_data

            # sleep after every 2rd call to be kind to the API
            if idx % 2 == 0:
                time.sleep(0.5)
        logger.info("Finished getting historical klines.")
        return output_data

    # TODO actually use these functions and state
    def change_state(self, state: str) -> bool:
        if state in State.__members__:
            self.state = State[state]
            return True
        return False

    def check_state(self) -> str:
        return self.state.name

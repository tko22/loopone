import hashlib
import hmac
import time
import asyncio
import aiohttp
from typing import Dict, Callable

import requests
from common import convert_dict_to_request_body
from enums import State, TradingType
from binance_enums import KlineIntervals
from exceptions import BinanceAPIException

API_URL = "https://api.binance.com/api"
STREAM_URL = "wss://stream.binance.com:9443/"
REQ_RATE_VIOLATION_CODE = 429
REQ_BAN_CODE = 418
DEFAULT_TIMEOUT = 10
PUBLIC_API_VERSION = "v1"
PRIVATE_API_VERSION = "v3"


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

            raise BinanceAPIException(response)
        return response.json()

    def _request(self, method: str, uri: str, signed: bool = True, **kwargs) -> None:
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

    def change_state(self, state: str) -> bool:
        if state in State.__members__:
            self.state = State[state]
            return True
        return False

    def check_state(self) -> str:
        return self.state.name

    # api wrappers
    def get_ticker_price(self, symbol: str) -> Dict:
        return self._get("ticker/price", params={"symbol": symbol})

    def get_ticker_24hr_change(self, symbol: str) -> Dict:
        """Get 24hr change given a symbol

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#24hr-ticker-price-change-statistics
        """
        return self._get("24hr", params={"symbol": symbol})

    def get_kline(
        self,
        symbol: str,
        interval: str = KlineIntervals.ONE_HOUR.value,
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
                "interval": interval,
                "startTime": start_time,
                "endTime": end_time,
                "limit": limit,
            },
        )

    async def get_ws_price_stream(self, symbol: str) -> aiohttp.ClientWebSocketResponse:
        lower_symbol = symbol.lower()
        async with self.async_session.ws_connect(
            f"{STREAM_URL}stream?streams=ethbtc@kline_1h"
        ) as ws:
            async for msg in ws:
                yield msg
        await self.async_session.close()

    async def close_session(self):
        print("Closing session...")
        await self.async_session.close()

import configparser
from typing import Dict, Tuple, List
from datetime import datetime

import pandas as pd
from marshmallow import Schema, fields, INCLUDE, post_dump
from mongoengine import connect

from .enums import KlineIntervals

DEFAULT_CREDS_FILE = "creds.ini"


class KlineDataSchema(Schema):
    class Meta:
        unknown = INCLUDE

    s = fields.Str(data_key="symbol")
    c = fields.Float(data_key="price")
    E = fields.Str(data_key="event_time")
    t = fields.Str(data_key="kline_start_time")
    T = fields.Str(data_key="kline_close_time")
    i = fields.Str(data_key="interval")
    f = fields.Integer(data_key="first_trade_id")
    l = fields.Integer(data_key="last_trade_id")
    o = fields.Float(data_key="open_prices")

    # @post_dump
    # def change_to_datetime(self, item):
    #     item["event_time"] = milli_to_date(float(item["event_time"]))


def convert_dict_to_request_body(payload: Dict) -> str:
    return "&".join(["{}={}".format(d[0], d[1]) for d in payload])


def get_credentials(file: str = DEFAULT_CREDS_FILE) -> Tuple:
    config = configparser.ConfigParser()
    config.read(file)
    credentials_section = config["credentials"]
    return (credentials_section["api_key"], credentials_section["api_secret"])


def get_mongo_credentials(file: str = DEFAULT_CREDS_FILE) -> Tuple:
    config = configparser.ConfigParser()
    config.read(file)
    mongo_section = config["mongo_creds"]
    return (mongo_section["mongo_db_name"], mongo_section["mongo_url"])


def milli_to_date(binance_time: int) -> datetime:
    """
    Convert binance milliseconds to datetime
    """
    return datetime.fromtimestamp(binance_time / 1000.0)


def interval_to_milli(interval: str = KlineIntervals.ONE_MIN.value) -> int:
    """Convert a Binance interval string to milliseconds
    :param interval: Binance interval string, e.g.: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
    :type interval: str
    :return:
        int value of interval in milliseconds
        None if interval prefix is not a decimal integer
        None if interval suffix is not one of m, h, d, w
    """
    seconds_per_unit = {"m": 60, "h": 60 * 60, "d": 24 * 60 * 60, "w": 7 * 24 * 60 * 60}
    try:
        if interval[-1] in seconds_per_unit:
            return (
                int(interval[0]) * seconds_per_unit[interval[-1]] * 1000
            )  # multiply by 1000 seconds for milli
        else:
            return None
    except ValueError:
        return None


def milli_to_str(time: int) -> str:
    """Convert milliseconds to date string format ex: 09/27/2018 16:20"""

    return milli_to_date(time).strftime("%m/%d/%y %H:%M")


def kline_bn_to_df(data: List) -> pd.DataFrame:
    """
    Convert Binance Kline data (2-D list) into a dataframe with the labeled columns
    """
    return pd.DataFrame(
        data,
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


def kline_bn_stream_to_dict(data: Dict) -> Dict:
    kline_data = data["k"]
    return {
        "symbol": data["s"],
        "price": kline_data["c"],
        "event_time": milli_to_date(data["E"]),
        "kline_start_time": milli_to_date(kline_data["t"]),
        "kline_close_time": milli_to_date(kline_data["T"]),
        "interval": kline_data["i"],
        "first_trade_id": kline_data["f"],
        "last_trade_id": kline_data["L"],
        "open_price": float(kline_data["o"]),
        "close_price": float(kline_data["c"]),
        "high_price": float(kline_data["h"]),
        "low_price": float(kline_data["l"]),
        "base_asset_volume": float(kline_data["v"]),
        "num_of_trades": kline_data["n"],
        "kline_closed": kline_data["x"],
        "quote_asset_volume": kline_data["q"],
        "taker_buy_base_asset_volume": kline_data["V"],
        "taker_buy_quote_asset_volume": kline_data["Q"],
    }


def connect_to_mongo() -> None:
    """Connect to MongoDB given the credentials in creds.ini"""
    (db_name, mongo_url) = get_mongo_credentials()
    connect(db_name, host=mongo_url)

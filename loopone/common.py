import configparser
from typing import Dict, Tuple
from datetime import datetime

import numpy as np
from marshmallow import Schema, fields, INCLUDE, post_dump


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


def get_credentials(file: str = "creds.ini") -> Tuple:
    config = configparser.ConfigParser()
    config.read(file)
    credentials_section = config["credentials"]
    return (credentials_section["api_key"], credentials_section["api_secret"])


def get_mongo_credentials(file: str = "creds.ini") -> Tuple:
    config = configparser.ConfigParser()
    config.read(file)
    mongo_section = config["mongo_creds"]
    return (mongo_section["mongo_db_name"], mongo_section["mongo_url"])


def milli_to_date(binance_time: int) -> datetime:
    return datetime.fromtimestamp(binance_time / 1000.0)


def kline_binance_to_dict(data: Dict) -> Dict:
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

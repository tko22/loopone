import configparser
from typing import Dict, Tuple
from datetime import datetime


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

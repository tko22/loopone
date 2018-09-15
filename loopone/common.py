import configparser
from typing import Dict
from datetime import datetime


def convert_dict_to_request_body(payload: Dict) -> str:
    return "&".join(["{}={}".format(d[0], d[1]) for d in payload])


def get_credentials(file: str = "creds.ini") -> Dict:
    config = configparser.ConfigParser()
    config.read(file)
    credentials_section = config["credentials"]
    return {
        "api_key": credentials_section["api_key"],
        "api_secret": credentials_section["api_key"],
    }


def milli_to_date(binance_time: int) -> datetime:
    return datetime.fromtimestamp(binance_time / 1000.0)

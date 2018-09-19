import csv

from binance import BinanceClient
from common import get_credentials, milli_to_date
from binance_enums import KlineIntervals

ONE_MIN_TIME_DIFF_THOUSAND_KLINE = 59940000

api_key, api_secret = get_credentials()
client = BinanceClient(api_key, api_secret)
data = client.get_kline("ethbtc", interval=KlineIntervals.ONE_MIN.value, limit=1000)

new_data = client.get_kline(
    "ethbtc",
    interval=KlineIntervals.ONE_MIN.value,
    start_time=data[0][6]
    - ONE_MIN_TIME_DIFF_THOUSAND_KLINE
    - 2 * 60 * 1000,  # without going down 2 klines, we can't get 1000
    end_time=data[0][6]
    - 60
    * 1000,  # make it include the kline before the start kline of the first request
    limit=1000,
)
new_data += data

added_datetime = [
    x + [milli_to_date(x[0]).ctime(), milli_to_date(x[6]).ctime()] for x in new_data
]


with open(
    f'ethbtc-{added_datetime[0][12].replace(" ", "-")}_{added_datetime[-1][12].replace(" ", "-")}.csv',
    "w",
    newline="",
) as csvfile:
    spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
    spamwriter.writerow(
        [
            "Open time",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "Close time",
            "Quote asset volume",
            "Number of trades",
            "Taker buy base asset volume",
            "Taker buy quote asset volume",
            "Ignore",
            "Open Datetime",
            "Closed Datetime",
        ]
    )

    spamwriter.writerows(added_datetime)

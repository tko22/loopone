import csv
import pandas as pd

from .gateways.binance import BinanceClient
from .common import get_credentials, milli_to_date
from .enums import KlineIntervals
from .finance.technicals import get_sma, generate_sma_list, generate_ema_list

ONE_MIN_TIME_DIFF_THOUSAND_KLINE = 60_000_000

api_key, api_secret = get_credentials()
client = BinanceClient(api_key, api_secret)
data = client.get_kline("ethbtc", interval=KlineIntervals.ONE_MIN.value, limit=1000)
x = client.get_historical_klines("ethbtc", interval=KlineIntervals.ONE_MIN.value)
import ipdb

ipdb.set_trace()

new_data = client.get_kline(
    "ethbtc",
    interval=KlineIntervals.ONE_MIN.value,
    start_time=data[0][0]
    - ONE_MIN_TIME_DIFF_THOUSAND_KLINE,  # without going down 2 klines, we can't get 1000
    end_time=data[0][6]
    - 60
    * 1000,  # make it include the kline before the start kline of the first request
    limit=1000,
)

print("middle", milli_to_date(new_data[-1][6]).strftime("%m/%d/%y %H:%M"))
print("middle_front", milli_to_date(data[0][0]).strftime("%m/%d/%y %H:%M"))
import ipdb

ipdb.set_trace()
new_data += data
df = pd.DataFrame(
    list(reversed(new_data)),
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
convert_open_time = lambda row: milli_to_date(row["open_time"]).strftime(
    "%m/%d/%y %H:%M"
)
convert_close_time = lambda row: milli_to_date(row["close_time"]).strftime(
    "%m/%d/%y %H:%M"
)

df["Open Datetime"] = df.apply(lambda row: convert_open_time(row), axis=1)
df["Closed Datetime"] = df.apply(lambda row: convert_close_time(row), axis=1)
df["sma_history"] = generate_sma_list(df["close_price"], 20)
df["ema_history"] = generate_ema_list(df["close_price"], df["sma_history"], 10)

df.to_excel(
    f'ethbtc-{milli_to_date(df["open_time"][0]).ctime().replace(" ", "-")}_{milli_to_date(df["close_time"][6]).ctime().replace(" ", "-")}.xlsx'
)

# with open(
#     f'ethbtc-{milli_to_date(df["open_time"][0]).ctime().replace(" ", "-")}_{milli_to_date(df["close_time"][6]).ctime().replace(" ", "-")}.csv',
#     "w",
#     newline="",
# ) as csvfile:
#     spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
#     spamwriter.writerow(
#         [
#             "Open time",
#             "Open",
#             "High",
#             "Low",
#             "Close",
#             "Volume",
#             "Close time",
#             "Quote asset volume",
#             "Number of trades",
#             "Taker buy base asset volume",
#             "Taker buy quote asset volume",
#             "Ignore",
#             "Open Datetime",
#             "Closed Datetime",
#         ]
#     )

#     spamwriter.writerows(added_datetime)

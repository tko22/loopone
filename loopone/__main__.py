import time
from datetime import datetime

from client import BinanceClient
from common import get_credentials, milli_to_date

import pprint


def main():
    creds = get_credentials()
    client = BinanceClient(api_key=creds["api_key"], api_secret=creds["api_secret"])
    initial_time = time.time()
    res = client.get_kline("VETETH", interval="1h", limit=100)
    import ipdb

    ipdb.set_trace()
    print(milli_to_date(res[0][0]).isoformat())
    # pprint.pprint(res)
    return
    while True:
        time.sleep(1)
        if time.time() - initial_time >= 60:
            break
        res = client._get("ticker/price", params={"symbol": "ETHBTC"})
        print(res["price"])


if __name__ == "__main__":
    main()

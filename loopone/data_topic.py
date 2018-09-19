from dataclasses import dataclass


@dataclass
class DataTopic(object):
    e = "24hrTicker"  # Event type
    E = 123456789  # Event time
    s = "BNBBTC"  # Symbol
    p = "0.0015"  # Price change
    P = "250.00"  # Price change percent
    w = "0.0018"  # Weighted average price
    x = "0.0009"  # Previous day's close price
    c = "0.0025"  # Current day's close price
    Q = "10"  # Close trade's quantity
    b = "0.0024"  # Best bid price
    B = "10"  # Best bid quantity
    a = "0.0026"  # Best ask price
    A = "100"  # Best ask quantity
    o = "0.0010"  # Open price
    h = "0.0025"  # High price
    l = "0.0010"  # Low price
    v = "10000"  # Total traded base asset volume
    q = "18"  # Total traded quote asset volume
    O = 0  # Statistics open time
    C = 86400000  # Statistics close time
    F = 0  # First trade ID
    L = 18150  # Last trade Id
    n = 18151  # Total number of trades
    # def __init(self, symbol: str, data):
    #     self.smbol = symbol
    #     self.data = data  # thinking Dataframe

    # def volume(self):
    #     pass

    # def history(self):
    #     pass

    # def current(self):
    #     pass

    # def twenty_hr_moving_average(self):
    #     pass

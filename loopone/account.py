import time
from collections import OrderedDict

from .enums import OrderSide

# under the assumption that our base asset is BTC
class AssetPositions(object):
    def __init__(self, asset: str, base_asset: str = "BTC"):
        self.asset = asset
        self.base_asset = base_asset
        self.total_quantity = 0
        self.total_value = 0  # maybe use it to calculate the BTC value
        self.avg_price = None
        self.positions = []  # TODO maybe make it a heap for better runtime?

    def addPosition(self, quantity: float, price: float, timestamp: time.time()):
        self.total_quantity += quantity
        # TODO include spread + fees
        self.positions.append((quantity, price, quantity * price, timestamp))

    def sell(self, quantity: float):
        """
        Return returns made from the sell 
        """
        self.total_quantity -= quantity

    def __repr__(self):
        return f"<AssetPostion {self.asset}/{self.base_asset}"


class Portfolio(object):
    def __init__(self, capital_base: float):
        self.starting_cash = capital_base
        self.portfolio_value = capital_base
        self.cash = capital_base  # cash as in BTC
        self.cash_flow = 0.0
        self.returns = 0.0
        self.positions = (
            OrderedDict()
        )  # holds ticker: [Postiion] with most recently updated ones at the back
        self.start_date = time.time()  # unix timestamp of the current time
        self.positions_value = 0.0
        self.positions_exposure = 0.0  # adding this for now

    def changePosition(
        self, asset: str, quantity: float, price: float, order_side: OrderSide
    ):
        total_value = price * quantity
        if order_side == OrderSide.SIDE_BUY:
            if total_value > self.cash:
                raise ValueError("Not enough Cash")
            new_pos = Position(asset, quantity, price)
            if asset in self.positions:
                self.positions[asset].append(new_pos)
            else:
                # first time position is made with asset
                self.positions[asset] = [new_pos]
        elif order_side == OrderSide.SIDE_SELL:
            pass

import time
from datetime import datetime
from collections import defaultdict

from loopone.enums import OrderSide, TradingType
from loopone.data_topic import DataTopic
from loopone.gateways.binance import BinanceClient
from loopone.models import KlineRecord, PaperTradeOrder

# TODO: make positions and portfolio persistant
class AssetPositions(object):
    """
    Position for an asset
    (under the assumption that our base asset is BTC)
    """

    def __init__(self, asset: str, base_asset: str = "BTC"):
        self.asset = asset
        self.base_asset = base_asset
        self.total_quantity = 0
        self.avg_price_bought = None
        self.positions = []  # TODO maybe make it a heap for better runtime?

    def add_position(
        self, quantity: float, price: float, timestamp: float = time.time()
    ):
        self.total_quantity += quantity
        # TODO include spread + fees
        self.positions.append((quantity, price, quantity * price, timestamp))

    def sell(self, quantity: float, price: float):
        """
        Return returns made from the sell 
        """
        self.total_quantity -= quantity

    def total_value(self, curr_asset_val: float) -> float:
        """
        Total Value based on current asset value passed in as parameter
        """
        return self.total_quantity * curr_asset_val

    def __repr__(self):
        return f"<AssetPostion {self.asset}/{self.base_asset}"


class Portfolio(object):
    def __init__(
        self,
        capital_base: float,
        client: BinanceClient,
        trading_type: TradingType = TradingType.PAPER,
    ):
        self._client = client

        self.starting_cash = capital_base
        self.cash = capital_base  # cash as in BTC
        self.cash_flow = 0.0
        self.asset_positions = {}

        self.start_date = time.time()  # unix timestamp of the current time
        self.positions_exposure = 0.0  # adding this for now

        self.trading_type = trading_type

    def change_position(
        self,
        asset: str,
        quantity: float,
        price: float,
        order_side: OrderSide,
        dt: DataTopic,
    ):
        total_value = price * quantity
        # TODO: validate inputs (i.e. whether asset is valid)

        # --------------------------------- #

        # for both sell and buy
        if self.trading_type == TradingType.PAPER:
            new_order = PaperTradeOrder(
                symbol=asset,
                time_executed=datetime.now(),
                quantity=0.3,
                market_volume=dt.quote_asset_volume,
                price=price,
                order_side=order_side.value,
            )
            new_order.save()

        if self.trading_type == TradingType.REAL_TRADE:
            pass

        # BUY
        if order_side == OrderSide.SIDE_BUY:
            if total_value > self.cash:
                raise ValueError(
                    f"Not enough Cash. Cannot buy {quantity} {asset} for {price}"
                )

            # create new AssetPositions for asset if DNE
            if self.asset_positions[asset] is None:
                self.asset_positions[asset] = AssetPositions(asset)

            self.asset_positions[asset].add_position(quantity=quantity, price=price)
            self.cash -= total_value

        # ---------------------------------- #
        # SELL
        if order_side == OrderSide.SIDE_SELL:
            if self.asset_positions[asset] is None:
                raise ValueError(
                    f"No positions in {asset}. Cannot sell {quantity} {asset}."
                )
            if self.asset_positions[asset].total_quantity < quantity:
                # total quantity of assets held is less than what you want to sell -> fail
                raise ValueError(
                    f"Total Quantity of {asset} held is {self.asset_positions[asset].total_quantity}. Cannot sell more than that ({quantity})."
                )

            # valid inputs, sell
            self.asset_positions[asset].sell(quantity, price)
            self.cash += total_value

    #  ---------------------------------- #
    # Functions that measure value of portfolio - subject to asset prices, which fluctuate
    # TODO: make more efficient besides recalculating value everytime
    async def get_portfolio_value(self) -> float:
        """
        Calculates value of portfolio (includes asset positions + cash)
        """
        assets_value = await self.get_asset_positions_value()
        return self.cash + assets_value

    async def get_asset_positions_value(self) -> float:
        """
        Calculates value of all asset positions held
        """
        total_val = 0.0
        for asset, asset_pos in self.asset_positions.items():
            asset_price = await self._client.get_ticker_price(
                asset + "btc"
            )  # get current price
            # addition of "btc" string is needed to include base asset
            # under assumption that base asset is BTC, calculates BTC value
            # TODO: change to be dynamic based on base_asset
            total_val += asset_pos.total_value(asset_price)

    async def get_returns(self) -> float:
        """
        Calculates returns of asset positions, based on investments put in
        """
        portfolio_val = await self.get_portfolio_value()
        return self.starting_cash - portfolio_val


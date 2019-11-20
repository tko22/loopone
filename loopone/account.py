import time
import logging
from datetime import datetime
from collections import defaultdict
from typing import Tuple, Dict

from loopone.enums import OrderSide, TradingType
from loopone.data_topic import DataTopic
from loopone.gateways.binance import BinanceClient
from loopone.models import KlineRecord, PaperTradeOrder
from uuid import uuid4

# TODO: make positions and portfolio persistant
class AssetPositions(object):
    """
    Position for an asset
    (under the assumption that our base asset is BTC)
    """

    def __init__(self, asset: str, base_asset: str = "BTC"):
        self.asset = asset
        self.base_asset = base_asset
        self.total_quantity: float = 0.0
        self.avg_price_bought = None
        self.positions = []  # TODO maybe make it a heap for better runtime?

    def buy(self, quantity: float, price: float, timestamp: float = time.time()):
        self.total_quantity += quantity
        # TODO include spread + fees
        self.positions.append(
            (OrderSide.SIDE_BUY, quantity, price, quantity * price, timestamp)
        )

    def sell(self, quantity: float, price: float, timestamp: float = time.time()):
        """
        Return returns made from the sell 
        """
        self.total_quantity -= quantity
        self.positions.append(
            (OrderSide.SIDE_SELL, quantity, price, quantity * price, timestamp)
        )

    def get_total_value(self, curr_asset_val: float) -> float:
        """
        Total Value based on current asset value passed in as parameter. Note curr_asset_val must be based on base asset
        """
        return self.total_quantity * curr_asset_val

    def get_return_details(self, curr_asset_val: float) -> Tuple:
        """
        Helper function: gets details on return of asset; value is based on base asset
        
        spent: amount spent buying asset
        sold: realized share value (in "cash" aka base asset)
        unrealized_share_val: amount of current shares held * curr value of asset
        total: unrealized + realized value of shares
        """
        # add up amount of base_asset spent
        spent = 0.0
        sold = 0.0
        for pos in self.positions:
            if pos[0] == OrderSide.SIDE_BUY:
                spent += pos[3]
            if pos[0] == OrderSide.SIDE_SELL:
                sold += pos[3]

        # present value of remaining shares
        unrealized_share_val = self.get_total_value(curr_asset_val)

        total = unrealized_share_val + sold  # realized + unrealized value

        return spent, sold, unrealized_share_val, total

    def get_returns(self, curr_asset_val: float) -> float:
        """
        Get Total Base Asset Return value
        """
        spent, _, _, total = self.get_return_details(curr_asset_val)
        return total - spent

    def get_percentage_return(self, curr_asset_val: float) -> float:
        """
        Get percentage return; value based on base asset
        """
        spent, _, _, total = self.get_return_details(curr_asset_val)
        return ((total - spent) / spent) * 100

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

        self.starting_cash: float = capital_base
        self.__cash: float = capital_base  # cash as in BTC
        self.cash_flow: float = 0.0
        self.asset_positions: Dict[AssetPositions] = {}

        self.start_date: datetime = datetime.now()  # unix timestamp of the current time
        self.positions_exposure: float = 0.0  # adding this for now

        self.trading_type: TradingType = trading_type
        self.session_id: str = str(uuid4())  # generate random uuid

        self.logger = logging.getLogger(__name__)
        self.logger.info(
            "Set up Portfolio %s starting at %s. Trading type: %s",
            self.session_id,
            self.start_date,
            self.trading_type,
        )

    def change_position(
        self, asset: str, quantity: float, order_side: OrderSide, dt: DataTopic
    ):
        self.logger.info(
            "%s %s %s",
            "Buying" if order_side == OrderSide.SIDE_BUY else "Selling",
            quantity,
            asset,
        )
        price = (
            dt.price
        )  # for paper trading purposes. Todo change this to the price when you actually buy it for real

        total_value = price * quantity
        # TODO: validate inputs (i.e. whether asset is valid)
        # 2) get price when you actually buy it if real

        # --------------------------------- #

        # for both sell and buy
        if self.trading_type == TradingType.PAPER:
            new_order = PaperTradeOrder(
                symbol=asset,
                time_executed=datetime.now(),
                quantity=quantity,
                market_volume=dt.quote_asset_volume,
                price=dt.price,  # for paper trading purposes
                order_side=order_side.value,
                session_id=self.session_id,
            )
            new_order.save()

        if self.trading_type == TradingType.REAL_TRADE:
            pass

        # BUY
        if order_side == OrderSide.SIDE_BUY:
            if total_value > self.__cash:
                raise ValueError(
                    f"Not enough Cash. Cannot buy {quantity} {asset} for {price}"
                )

            # create new AssetPositions for asset if DNE
            if self.asset_positions.get(asset) is None:
                self.asset_positions[asset] = AssetPositions(asset)

            self.asset_positions[asset].buy(quantity=quantity, price=price)
            self.__cash -= total_value

        # ---------------------------------- #
        # SELL
        if order_side == OrderSide.SIDE_SELL:
            if self.asset_positions.get(asset) is None:
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
            self.__cash += total_value

    #  ---------------------------------- #
    # Functions that measure value of portfolio - subject to asset prices, which fluctuate
    # TODO: make more efficient besides recalculating value everytime
    async def get_portfolio_value(self) -> float:
        """
        Calculates value of portfolio (includes asset positions + cash)
        """
        assets_value = await self.get_asset_positions_value()
        return self.__cash + assets_value

    async def get_asset_positions_value(self) -> float:
        """
        Calculates value of all asset positions held
        """
        total_val = 0.0
        for asset, asset_pos in self.asset_positions.items():
            res = await self._client.get_ticker_price(asset)  # get current price
            asset_price = float(res.get("price"))

            # addition of "btc" string is needed to include base asset
            # under assumption that base asset is BTC, calculates BTC value
            # TODO: change to be dynamic based on base_asset
            total_val += asset_pos.get_total_value(asset_price)
        return total_val

    async def get_returns(self) -> float:
        """
        Calculates returns of asset positions, based on investments put in
        """
        portfolio_val = await self.get_portfolio_value()
        return self.starting_cash - portfolio_val

    async def get_percentage_returns(self) -> float:
        """
        Calculates Percentage returns of asset positions, based on investments put in
        """
        returns = await self.get_returns()
        return (returns / self.starting_cash) * 100

    @property
    def cash(self):
        return self.__cash

    def __str__(self):
        return f"<Portfolio {self.session_id} {self.trading_type.value}>"

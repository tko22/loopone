from mongoengine.fields import (
    StringField,
    IntField,
    DateTimeField,
    BooleanField,
    FloatField,
)
import mongoengine


class KlineRecord(mongoengine.DynamicDocument):
    """Kline Record that's streamed from Binance"""

    symbol = StringField(required=True)
    price = StringField(required=True)
    event_time = DateTimeField()
    kline_start_time = DateTimeField()
    kline_close_time = DateTimeField()
    interval = StringField()
    first_trade_id = IntField()
    last_trade_id = IntField()
    open_price = FloatField()
    close_price = FloatField()
    high_price = FloatField()
    low_price = FloatField()
    base_asset_volume = FloatField()  # string in streamed data
    num_of_trades = IntField()
    kline_closed = BooleanField()
    quote_asset_volume = StringField()
    taker_buy_base_asset_volume = StringField()
    taker_buy_quote_asset_volume = StringField()
    twenty_hr_moving_avg = FloatField()

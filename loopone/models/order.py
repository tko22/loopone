from mongoengine.fields import (
    StringField,
    IntField,
    DateTimeField,
    BooleanField,
    FloatField,
)
import mongoengine


class Order(mongoengine.DynamicDocument):
    symbol = StringField(required=True)
    quantity = FloatField(required=True)
    time_executed = DateTimeField(required=True)
    quantity = FloatField(required=True)
    order_side = StringField(required=True)
    cost_basis = FloatField()  # average price for order, which binance gives to us
    order_fee = FloatField()
    market_volume = FloatField()
    # allow subclasses
    meta = {"allow_inheritance": True}


class PaperTradeOrder(Order):
    price = FloatField(required=True)
    session_id = StringField(required=True)


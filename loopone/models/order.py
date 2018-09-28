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
    time_executed = DateTimeField()
    cost_basis = FloatField()
    quantity = FloatField()
    fee = FloatField()


class PaperTradeOrder(Order):
    pass


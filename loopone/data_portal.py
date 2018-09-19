import json
from typing import Dict

"""
Make requests for additional information asynchrounous, adding them into a list of tasks
"""


class DataPortal(object):
    def __init__(self, producer, symbol: str, collect: bool = False):
        self.symbol = symbol
        self.producer = producer
        self.collect = collect  # change this to trading type later

    async def data_stream(self) -> Dict:
        # TODO make this return a DataTopic instead
        async for msg in self.producer:
            data = json.loads(msg.data)

            yield json.loads(msg.data)


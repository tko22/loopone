from typing import Dict

"""
Make requests for additional information asynchrounous, adding them into a list of tasks
"""


class DataPortal(object):
    def __init__(self, producer, symbol):
        self.symbol = symbol
        self.producer = producer

    async def data_stream(self) -> Dict:
        # TODO make this return a DataTopic instead
        async for msg in self.producer:
            yield msg


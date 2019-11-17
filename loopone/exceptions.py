from abc import abstractmethod


class BinanceAPIException(Exception):
    def __init__(self, response):
        self.code = 0
        self.status_code = 500  # default
        self.response = response
        self.message = ""

    def populate(self, response):
        self.response = response
        self.request = getattr(response, "request", None)

    def __str__(self):  # pragma: no cover
        return f"APIError(code={self.status_code}): {self.message}"


class BinanceAsyncAPIException(BinanceAPIException):
    def __init__(self, response, json_res, message):
        self.message = message
        self.status_code = response.status
        self.populate(response)

        if json_res is not None:
            self.code = json_res["code"]


class BinanceRegAPIException(BinanceAPIException):
    def __init__(self, response):
        try:
            json_res = response.json()
        except ValueError:
            self.message = f"Invalid JSON error message from Binance: {response.text}"
        else:
            self.code = json_res["code"]
            self.message = json_res["msg"]

        self.status_code = response.status_code
        self.populate(response)

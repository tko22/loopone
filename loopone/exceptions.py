class BinanceAPIException(Exception):
    def __init__(self, response):
        self.code = 0
        try:
            json_res = response.json()
        except ValueError:
            self.message = f"Invalid JSON error message from Binance: {response.text}"
        else:
            self.code = json_res["code"]
            self.message = json_res["msg"]
        self.status_code = response.status_code
        self.response = response
        self.request = getattr(response, "request", None)

    def __str__(self):  # pragma: no cover
        return f"APIError(code={self.status_code}): {self.message}"

from enum import Enum


class State(Enum):
    DEV = "DEV"
    RUNNING = "RUNNING"
    STANDBY = "STANDBY"


class TradingType(Enum):
    PAPER = "PAPER"
    BACKTEST = "BACKTEST"
    REAL_TRADE = "REAL_TRADE"

import sys
import logging

import colorlog
from .__main__ import main

DEFAULT_LOG_FILE = "loopone.log"
DEFAULT_FORMATTER = colorlog.ColoredFormatter(
    "[%(asctime)s: %(log_color)s%(levelname)s%(reset)s]: [%(name)s]: %(log_color)s%(message)s",
    reset=True,
)

# setup logging
logger = logging.getLogger()  # get root logger
fh = logging.FileHandler(DEFAULT_LOG_FILE)
logger.setLevel(logging.DEBUG)
fh.setFormatter(DEFAULT_FORMATTER)

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(DEFAULT_FORMATTER)
logger.setLevel(logging.INFO)
logger.addHandler(fh)
logger.addHandler(ch)

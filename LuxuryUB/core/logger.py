import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    format="[%(levelname)s- %(asctime)s]- %(name)s- %(message)s- %(filename)s- %(lineno)d",
    level=logging.INFO,
    datefmt="%H:%M:%S",
    handlers=[
        RotatingFileHandler("bot.log", maxBytes=5000000, backupCount=1, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
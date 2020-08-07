import logging
from logging.handlers import TimedRotatingFileHandler
import datetime

def configLogger(loggername):
    now = datetime.datetime.now()
    logger = logging.getLogger(loggername)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s: %(name)s: %(message)s',datefmt='%d/%m/%Y %I:%M:%S %p')
    fileHandler = logging.FileHandler('./logs/pod.log.{today}'.format(today=now.strftime("%d%m%Y")))
##    handler = TimedRotatingFileHandler("./logs/pod.log", when="midnight",interval=1)
##    handler.suffix = "%d%m%Y"
    fileHandler.setFormatter(formatter)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger


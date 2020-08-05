import logging

def configLogger(loggername):
    logger = logging.getLogger(loggername)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s: %(name)s: %(message)s',datefmt='%d/%m/%Y %I:%M:%S %p')
    fileHandler = logging.FileHandler('hist.log')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger


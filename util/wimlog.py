import logging

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',filename='fulltime.log',level=logging.INFO)


def info(msg):
    logging.info(msg)

def debug(msg):
    logging.info(msg)

def error(msg):
    logging.info(msg)
# Format copied from: https://stackoverflow.com/a/69989304/13244782
#handler = logging.FileHandler(filename="log.log", mode="w", encoding="utf-8")
#formatter = logging.Formatter(fmt='[%(levelname)s %(asctime)s %(filename)s->%(funcName)s():%(lineno)s]: %(message)s')
#
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)
#
#handler.setFormatter(formatter)
#logger.addHandler(handler)
#logger.setLevel(logging.DEBUG)

# https://stackoverflow.com/a/20112491/13244782
import logging
logger = logging.getLogger(__name__)
#FORMAT = '%(message)s'
FORMAT ='[%(levelname)s %(asctime)s %(filename)s->%(funcName)s():%(lineno)s]: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger.setLevel(logging.DEBUG)
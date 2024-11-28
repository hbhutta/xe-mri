import logging
logger = logging.getLogger(__name__)
#FORMAT = '%(message)s'
FORMAT ='[%(levelname)s %(asctime)s %(filename)s->%(funcName)s():%(lineno)s]: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger.setLevel(logging.DEBUG)
""" shell functions. """

import logging
import os

from ob import k
from ob.utl import cdir, hd

logfiled = ""

def init():
    k.register(log_handler)

class DumpHandler(logging.StreamHandler):

    """ handles nothing. """

    propagate = False

    def emit(self, record):
        pass

def level(loglevel="", logdir="", logfile="obot.log", nostream=False):
    """ initiate logging. """
    global logfiled
    if not loglevel:
        loglevel = "error"
    logdir = k.cfg.logdir or logdir or os.path.join(hd(".obot"), "logs")
    logfile = logfiled = os.path.join(logdir, logfile)
    if not os.path.exists(logfile):
        cdir(logfile)
    datefmt = '%H:%M:%S'
    format_time = "%(asctime)-8s %(message)-70s"
    format_plain = "%(message)-0s"
    loglevel = loglevel.upper()
    logger = logging.getLogger("")
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    try:
        logger.setLevel(loglevel)
    except ValueError:
        pass
    formatter = logging.Formatter(format_plain, datefmt)
    if nostream:
        dhandler = DumpHandler()
        dhandler.propagate = False
        dhandler.setLevel(loglevel)
        logger.addHandler(dhandler)
    else:
        handler = logging.StreamHandler()
        handler.propagate = False
        handler.setFormatter(formatter)
        try:
            handler.setLevel(loglevel)
            logger.addHandler(handler)
        except ValueError:
            logging.warn("worng level %s" % loglevel)
            loglevel = "error"
    formatter2 = logging.Formatter(format_time, datefmt)
    filehandler = logging.handlers.TimedRotatingFileHandler(logfile, 'midnight')
    filehandler.propagate = False
    filehandler.setFormatter(formatter2)
    filehandler.setLevel(loglevel)
    logger.addHandler(filehandler)
    return logger


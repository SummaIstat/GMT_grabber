import logging
import sys
from datetime import datetime


def setup_logger():
    if len(logging.getLogger().handlers) > 0:
        return None
    PROGRAM_NAME = "GMT_grabber"
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logFormatter = logging.Formatter("%(asctime)s - %(module)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    now = datetime.now()
    dateTime = now.strftime("%Y-%m-%d_%H_%M_%S")
    LOG_FILE_NAME = "logs/log_" + PROGRAM_NAME + "_" + dateTime + ".log"
    fileHandler = logging.FileHandler(LOG_FILE_NAME)
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)
    #return logger


#logger = setup_logger("GMT_grabber_logger")
#logger.info("GMT_grabber logger has been initialized")

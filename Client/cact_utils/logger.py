import datetime as time
import logging
logger = logging.getLogger(__name__)


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    BBLACK = '\033[90m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log_with_color(message, color):
    now = time.datetime.now()
    t = now.strftime("%m-%d-%Y %X")
    logger.info(f"{color}[{t}] {message}{BColors.RESET}")


def success(message):
    log_with_color(message, BColors.SUCCESS)


def warning(message):
    log_with_color(message, BColors.WARNING)


def error(message):
    log_with_color(message, BColors.ERROR)


def bold(message):
    log_with_color(message, BColors.BOLD)


def log(message):
    log_with_color(message, BColors.RESET)


def debug(message):
    now = time.datetime.now()
    t = now.strftime("%m-%d-%Y %X")
    logger.info(f"{BColors.BBLACK}[{t}] {message}{BColors.RESET}")
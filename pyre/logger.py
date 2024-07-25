import logging
import sys

# Define some colors
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# The background is set with 40 plus the number of the color, and the foreground with 30

# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, color):
    return COLOR_SEQ % (30 + color) + message + RESET_SEQ

COLORS = {
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': BLUE,
    'CRITICAL': MAGENTA,
    'ERROR': RED
}

class ColoredLogger(logging.Formatter):
    def __init__(self, msg, date_format):
        logging.Formatter.__init__(self, msg, date_format)

    def format(self, record):
        levelname = record.levelname
        if levelname in COLORS:
            record.msg = formatter_message(record.msg, COLORS[levelname])
        return logging.Formatter.format(self, record)

# Create a logger
logger = logging.getLogger('PYRE')
logger.setLevel(logging.DEBUG)

# Create a handler
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(ColoredLogger('[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s', "%Y-%m-%d %H:%M:%S"))

# Add the handler to the logger
logger.addHandler(handler)
LOG = logger

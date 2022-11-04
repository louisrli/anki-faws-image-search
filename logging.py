import logging
import sys

logger = logging.getLogger("faws")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

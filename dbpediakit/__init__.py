import logging
import sys

# use stderr for progress monitoring to be able to use stdout for piping CSV
# stream to postgresql for instance
logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                    format='%(levelname)s\t%(asctime)s\t%(message)s')

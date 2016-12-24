import logging
import sys
import socket
from scrapy.cmdline import execute
from scrapy.settings.default_settings import LOG_FORMAT

formatter = logging.Formatter(LOG_FORMAT)
handler = logging.StreamHandler()
handler.setFormatter(formatter)

if ''.join(sys.argv).find('INFO') > 0:
    handler.setLevel(logging.INFO)
else:
    handler.setLevel(logging.DEBUG)

if socket.gethostname().startswith('YieldNull'):
    logging.getLogger().addHandler(handler)

execute()

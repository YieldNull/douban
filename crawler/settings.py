# -*- coding: utf-8 -*-

# Scrapy settings for crawler project

BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders', 'tests.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

ROBOTSTXT_OBEY = False
COOKIES_ENABLED = False

LOGIN_ENABLED = False
LOGIN_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
LOGIN_COOKIE = ''

CONCURRENT_REQUESTS = 4 if LOGIN_ENABLED else 16

CONCURRENT_REQUESTS_PER_DOMAIN = 4 if LOGIN_ENABLED else 16

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
}

DOWNLOADER_MIDDLEWARES = {
    'crawler.middlewares.DownloaderMiddleware': 544,
}

ITEM_PIPELINES = {
    'crawler.pipelines.MoviePipeline': 300,
    'crawler.pipelines.SeedPipeline': 301,
}

MONGO_URI = 'mongodb://localhost:27017'
MONGO_DATABASE = 'douban'

LOG_FILE = 'douban.log'

import logging
from scrapy.settings.default_settings import LOG_FORMAT

formatter = logging.Formatter(LOG_FORMAT)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

logging.getLogger().addHandler(handler)

# Scrapy settings for crawler project

BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders', 'tests.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

ROBOTSTXT_OBEY = False
COOKIES_ENABLED = False

LOGIN_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
LOGIN_COOKIE = 'ue="isso_yieldnull@163.com"; dbcl2="155416755:shAzB/1dz2E"; bid=oO6QUb-aIMc; ps=y; ap=1; ck=MzAm; push_noty_num=0; push_doumail_num=0'

CONCURRENT_REQUESTS = 4

CONCURRENT_REQUESTS_PER_DOMAIN = 4

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

SQLITE_DATABASE = "douban.db"

LOG_FILE = 'douban.log'

# Scrapy settings for crawler project

BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders', 'tests.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

ROBOTSTXT_OBEY = False
COOKIES_ENABLED = False

LOGIN_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
LOGIN_COOKIE = ''

CONCURRENT_REQUESTS = 1

CONCURRENT_REQUESTS_PER_DOMAIN = 1

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
    'crawler.pipelines.ActorPipeline': 302
}

MONGO_URI = 'mongodb://localhost:27017'
MONGO_DATABASE = 'douban'

SQLITE_DATABASE = "douban.db"

LOG_FILE = 'douban.log'

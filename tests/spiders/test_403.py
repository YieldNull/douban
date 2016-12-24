from scrapy import Spider
import logging


# 测试 DownloaderMiddleware 处理 403,(close spider)
# 先运行 server_403.py

class Test403(Spider):
    name = 'test_403'

    start_urls = ['http://localhost:5000/?i={:d}'.format(i) for i in range(2000)]

    def parse(self, response):
        logging.info(response.url) # 4+10 times
        yield None

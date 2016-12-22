from scrapy import Spider


# 测试 DownloaderMiddleware 处理 403
# 先运行 http_server

class Test403(Spider):
    name = 'test403'

    start_urls = ['http://localhost:5000']

    def parse(self, response):
        yield {'test': 403}

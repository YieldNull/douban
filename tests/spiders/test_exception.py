from scrapy import Spider


class TestException(Spider):
    name = 'test_exception'

    start_urls = ['https://www.baidu.com']

    def parse(self, response):
        raise AttributeError()

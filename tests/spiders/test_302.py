from scrapy import Request

from crawler.spiders.movie import MovieSpider


class Test302(MovieSpider):
    name = 'test_302'

    def start_requests(self):
        yield Request(url='http://localhost:5000/', meta={'mid': 123455, 'login': False})
        yield Request(url='http://localhost:5000/sorry', meta={'mid': 123455, 'login': True})  # raise close spider
        yield Request(url='http://localhost:5000/3', meta={'mid': 123455, 'login': True})
        yield Request(url='http://localhost:5000/4', meta={'mid': 123455, 'login': False})

from scrapy import Item

from crawler.spiders.seeds import SeedSpider
from . import fake_response_from_file
import unittest


class SeedSpiderTest(unittest.TestCase):
    def test_parse_api(self):
        response = fake_response_from_file('files/api.json', meta={'start': 0, 'tag': 2016, 'tid': 21212})

        spider = SeedSpider()
        for item in spider.parse_api(response):
            if isinstance(item, Item):
                self.assertTrue(len(item['mids']) > 0)

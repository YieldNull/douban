from scrapy.exceptions import CloseSpider
from crawler.items import Actor404Item
from crawler.spiders.actor import ActorSpider
from tests import fake_response_from_file

import unittest


class ActorSpiderTest(unittest.TestCase):
    def setUp(self):
        self.spider = ActorSpider()
        self.meta = {'start': 0, 'aid': 21212}  # 必要信息，随便伪造一个

    def test_no_title(self):
        response = fake_response_from_file('files/ip_restricted.html', meta=self.meta)

        self.assertRaises(CloseSpider, next, self.spider.parse(response))

    def test_no_total(self):
        response = fake_response_from_file('files/actor_no_total.html', meta=self.meta)

        g = self.spider.parse(response)

        self.assertIsInstance(next(g), Actor404Item)
        self.assertRaises(StopIteration, next, g)

    def test_one_page(self):
        response = fake_response_from_file('files/actor_one_page.html', meta=self.meta)

        g = self.spider.parse(response)

        self.assertEqual(len(next(g)['mids']), 2)
        self.assertRaises(StopIteration, next, g)

    def test_multi_page(self):
        response = fake_response_from_file('files/actor_multi_page.html', meta=self.meta)

        g = self.spider.parse(response)

        self.assertEqual(len(next(g)['mids']), 25)

        request = next(g)
        self.assertEqual(request.meta['start'], 25)
        self.assertRaises(StopIteration, next, g)

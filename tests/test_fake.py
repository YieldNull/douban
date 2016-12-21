import unittest
import requests

import crawler.fake as fake

from crawler.spiders.movie import MovieSpider

from . import fake_response_from_url


class TestFakeBasics(unittest.TestCase):
    def setUp(self):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
        }

    def test_rand_cookie(self):
        """
        测试伪造的Cookie是否可以使用
        :return:
        """
        headers = self.headers.copy()
        headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) ' \
                                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'

        headers['Cookie'] = fake.rand_cookie()

        resp = requests.get('http://localhost:5000', headers=headers)
        self.assertNotEqual(403, resp.status_code)

    def test_user_agents(self):
        """
        测试User-Agent池中的Agent是否能够成功访问电脑版网页，并成功获得数据
        :return:
        """
        headers = self.headers.copy()
        headers['Cookie'] = fake.rand_cookie()
        headers['Referer'] = 'https://movie.douban.com/'

        from crawler.fake import USER_AGENTS

        for agent in USER_AGENTS:
            headers['User-Agent'] = agent

            resp = fake_response_from_url('https://movie.douban.com/subject/26362351/', headers=headers)
            self.assertNotEqual(403, resp.status)

            spider = MovieSpider()
            for item in spider.parse(resp):
                self.assertIsNotNone(item['rating'])

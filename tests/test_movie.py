from crawler.items import MovieItem
from crawler.spiders.movie import MovieSpider
from tests import fake_response_from_file, fake_response_from_url
import unittest

import os
from os.path import isfile, join


class MovieSpiderTest(unittest.TestCase):
    def test_movie(self):
        d = os.path.dirname(os.path.realpath(__file__))

        for file in os.listdir(join(d, 'files')):
            path = join(d, join('files', file))

            if isfile(path) and file.startswith('movie_') and path.endswith('.html'):
                response = fake_response_from_file(path)

                spider = MovieSpider()
                g = spider.parse(response)
                self.assertIsInstance(next(g), MovieItem)

    def test_latest(self):
        response = fake_response_from_url('https://movie.douban.com/subject/26877237/')
        spider = MovieSpider()
        g = spider.parse(response)

        item = next(g)
        self.assertIsInstance(item, MovieItem)

        print(item)

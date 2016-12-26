from scrapy import Item

from crawler.spiders.movie import MovieSpider
from . import fake_response_from_file
import unittest

import os
from os.path import isfile, join


class MovieSpiderTest(unittest.TestCase):
    def test_movie(self):

        for file in os.listdir('files'):
            path = join('files', file)
            if isfile(path) and file.startswith('movie_') and path.endswith('.html'):
                response = fake_response_from_file(path, meta={'mid': 2123123, 'login': False})

                spider = MovieSpider()
                for item in spider.parse(response):
                    print(item)

                print(file)

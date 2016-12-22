# -*- coding: utf-8 -*-

import pymongo

from pymongo.errors import DuplicateKeyError
from scrapy.exceptions import DropItem

from crawler.intermedia import Actor, Movie
from peewee import IntegrityError, DoesNotExist

from crawler.items import Movie404Item
from crawler.spiders.movie import MovieSpider
from crawler.spiders.seeds import SeedSpider

import logging


class SeedPipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        if spider.name != SeedSpider.name:
            return item

        for mid in item['mids']:
            try:
                Movie.create(mid=mid)
            except IntegrityError:
                continue

        return item


class MoviePipeline(object):
    collection_name = 'movie'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.db.movie.create_index([('mid', pymongo.ASCENDING)], unique=True)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if spider.name != MovieSpider.name:
            return item

        mid = item['mid']

        if isinstance(item, Movie404Item):
            Movie.update(require_login=True).where(Movie.mid == mid).execute()
            return item

        self._store_actors(item['directors'])
        self._store_actors(item['writers'])
        self._store_actors(item['casts'])

        self._store_movies(mid, item['recommendations'])
        data = dict(item)
        data.pop('recommendations')

        Movie.update(crawled=True).where(Movie.mid == mid).execute()

        try:
            self.db[self.collection_name].insert(data)
        except DuplicateKeyError:
            return DropItem('Mongodb: DuplicateKey: {:d}'.format(mid))
        else:
            return item

    @staticmethod
    def _store_actors(actors):
        for (aid, actor) in actors:
            if aid > 0:
                try:
                    Actor.create(aid=aid)
                except IntegrityError:
                    continue

    @staticmethod
    def _store_movies(source, movies):
        for mid in movies:
            mid = int(mid)
            try:
                Movie.get(Movie.mid == mid)
            except DoesNotExist:
                logging.info('Got a new movie not in db:{:d}. From:{:d}'.format(mid, source))
                Movie.create(mid=mid)

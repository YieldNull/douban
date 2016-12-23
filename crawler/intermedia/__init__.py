from peewee import SqliteDatabase, Model
from scrapy.conf import settings

db = SqliteDatabase(settings.get('SQLITE_DATABASE', 'peewee.db'))


class BaseModel(Model):
    class Meta:
        database = db


from crawler.intermedia.models import Movie, Actor

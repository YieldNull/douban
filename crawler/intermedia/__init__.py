from peewee import SqliteDatabase, Model
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

db = SqliteDatabase(settings.get('SQLITE_DATABASE', 'peewee.db'))


class BaseModel(Model):
    class Meta:
        database = db


from crawler.intermedia.models import Movie, Actor

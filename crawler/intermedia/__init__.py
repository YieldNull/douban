from peewee import SqliteDatabase, Model

db = SqliteDatabase('douban.db')


class BaseModel(Model):
    class Meta:
        database = db


from crawler.intermedia.models import Movie, Actor

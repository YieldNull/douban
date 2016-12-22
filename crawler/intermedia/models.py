from peewee import IntegerField, BooleanField

from crawler.intermedia import db, BaseModel


class Movie(BaseModel):
    mid = IntegerField(primary_key=True)
    crawled = BooleanField(default=False)
    require_login = BooleanField(default=False)


class Actor(BaseModel):
    aid = IntegerField(primary_key=True)
    crawled = BooleanField(default=False)


db.create_tables([Movie, Actor], safe=True)

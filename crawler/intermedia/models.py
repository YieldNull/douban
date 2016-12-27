from peewee import IntegerField, BooleanField

from crawler.intermedia import db, BaseModel


class Movie(BaseModel):
    TYPE_NORMAL = 0
    TYPE_LOGIN = 1
    TYPE_BROKEN = 2

    mid = IntegerField(primary_key=True)
    crawled = BooleanField(default=False)
    type = IntegerField(default=TYPE_NORMAL)

    def require_login(self):
        return self.type == self.TYPE_LOGIN


class Actor(BaseModel):
    TYPE_NORMAL = 0
    TYPE_BROKEN = 1

    aid = IntegerField(primary_key=True)
    crawled = BooleanField(default=False)
    type = IntegerField(default=TYPE_NORMAL)


db.create_tables([Movie, Actor], safe=True)

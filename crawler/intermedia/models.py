from peewee import IntegerField, BooleanField

from crawler.intermedia import db, BaseModel


class Movie(BaseModel):
    """
    全部爬完之后
    常规       crawled:True require_login:False
    需要登录   crawled:True require_login:True
    """
    mid = IntegerField(primary_key=True)
    crawled = BooleanField(default=False)
    require_login = BooleanField(default=False)


class Actor(BaseModel):
    aid = IntegerField(primary_key=True)
    crawled = BooleanField(default=False)


db.create_tables([Movie, Actor], safe=True)

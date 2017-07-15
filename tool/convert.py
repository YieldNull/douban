from peewee import Model, PrimaryKeyField, IntegerField, \
    CharField, TextField, MySQLDatabase, FloatField, CompositeKey, \
    ForeignKeyField, IntegrityError

from pymongo import MongoClient

db = MySQLDatabase('database', host="localhost", port=3306, user="user", passwd="passwd", charset='utf8mb4')


class BaseModel(Model):
    class Meta:
        database = db


class Movie(BaseModel):
    id = IntegerField(primary_key=True)
    subtype = IntegerField()
    title = TextField()
    poster = TextField()
    summary = TextField()
    original_title = CharField(null=True)
    year = IntegerField()
    duration = IntegerField(null=True)
    languages = CharField(null=True)
    douban_site = CharField(null=True)
    website = TextField(null=True)
    imdb = CharField(null=True)
    season = IntegerField(null=True)
    seasons_count = IntegerField(null=True)
    episodes_count = IntegerField(null=True)


class Rating(BaseModel):
    mid = ForeignKeyField(Movie, to_field=Movie.id, primary_key=True)
    star1 = FloatField()
    star2 = FloatField()
    star3 = FloatField()
    star4 = FloatField()
    star5 = FloatField()
    count = IntegerField()
    rating = FloatField()


class Aka(BaseModel):
    mid = ForeignKeyField(Movie, to_field=Movie.id)
    name = CharField()

    class Meta:
        primary_key = CompositeKey('mid', 'name')


class Genre(BaseModel):
    id = PrimaryKeyField()
    name = CharField(unique=True)


class Celebrity(BaseModel):
    id = PrimaryKeyField()
    cid = IntegerField(null=True)
    name = CharField()

    class Meta:
        indexes = (
            (('cid', 'name'), True),
        )


class Country(BaseModel):
    id = PrimaryKeyField()
    name = CharField(unique=True)


class Pubdate(BaseModel):
    id = PrimaryKeyField()
    date = CharField()


class MovieGenre(BaseModel):
    mid = ForeignKeyField(Movie, to_field=Movie.id)
    gid = ForeignKeyField(Genre, to_field=Genre.id)

    class Meta:
        primary_key = CompositeKey('mid', 'gid')


class MovieDirector(BaseModel):
    mid = ForeignKeyField(Movie, to_field=Movie.id)
    cid = ForeignKeyField(Celebrity, to_field=Celebrity.id)

    class Meta:
        primary_key = CompositeKey('mid', 'cid')


class MovieWriter(BaseModel):
    mid = ForeignKeyField(Movie, to_field=Movie.id)
    cid = ForeignKeyField(Celebrity, to_field=Celebrity.id)

    class Meta:
        primary_key = CompositeKey('mid', 'cid')


class MovieActor(BaseModel):
    mid = ForeignKeyField(Movie, to_field=Movie.id)
    cid = ForeignKeyField(Celebrity, to_field=Celebrity.id)

    class Meta:
        primary_key = CompositeKey('mid', 'cid')


class MovieCountry(BaseModel):
    mid = ForeignKeyField(Movie, to_field=Movie.id)
    cid = ForeignKeyField(Country, to_field=Country.id)

    class Meta:
        primary_key = CompositeKey('mid', 'cid')


class MoviePubdate(BaseModel):
    mid = ForeignKeyField(Movie, to_field=Movie.id)
    pid = ForeignKeyField(Pubdate, to_field=Pubdate.id)

    class Meta:
        primary_key = CompositeKey('mid', 'pid')


def import_data():
    client = MongoClient()
    db = client['douban_stable']

    counter = 0
    for m in db.movie.find():
        counter += 1
        if counter % 100 == 0:
            print(counter)

        mid = m['mid']

        Movie.create(id=m['mid'], subtype=1 if m['subtype'] == 'movie' else 0,
                     title=m['title'], poster=m['poster'],
                     summary=m['summary'], original_title=m['original_title'],
                     year=m['year'], duration=m['duration'],
                     languages=m['languages'], douban_site=m['douban_site'],
                     website=m['website'], imdb=m['imdb'],
                     season=m['season'], seasons_count=m['seasons_count'],
                     episodes_count=m['episodes_count'])

        try:
            ratings = m['rating_map']
            if len(ratings) == 5:
                Rating.create(mid=mid, star1=ratings[0], star2=ratings[1],
                              star3=ratings[2], star4=ratings[3], star5=ratings[4],
                              count=m['rating_count'], rating=m['rating'])

            akas = m['aka']
            if akas:
                for aka in set(akas):
                    Aka.create(mid=mid, name=aka)

            genres = m['genres']
            if genres:
                for genre in set(genres):
                    g, _ = Genre.get_or_create(name=genre)
                    MovieGenre.create(mid=mid, gid=g.id)

            directors = m['directors']
            if directors:
                for director in directors:
                    d = Celebrity.create(cid=director[0], name=director[1])
                    MovieDirector.create(mid=mid, cid=d.id)

            writers = m['writers']
            if writers:
                for writer in writers:
                    w = Celebrity.create(cid=writer[0], name=writer[1])
                    MovieWriter.create(mid=mid, cid=w.id)

            casts = m['casts']
            if casts:
                for actor in casts:
                    a = Celebrity.create(cid=actor[0], name=actor[1])
                    MovieActor.create(mid=mid, cid=a.id)

            countries = m['countries']
            if countries:
                for country in countries:
                    c, _ = Country.get_or_create(name=country)
                    MovieCountry.create(mid=mid, cid=c.id)

            pubdates = m['pubdates']
            if pubdates:
                for pubdate in pubdates:
                    p = Pubdate.create(date=pubdate)
                    MoviePubdate.create(mid=mid, pid=p.id)
        except IntegrityError:
            continue
        except Exception as e:
            print(m['mid'])
            raise e


# change mysql default encoding to utf8mb4

if __name__ == '__main__':
    db.create_tables(
        [Movie, Rating, Aka, Genre, Celebrity,
         Country, Pubdate, MovieGenre, MovieDirector, MovieWriter,
         MovieActor, MovieCountry, MoviePubdate], safe=True)

    import_data()

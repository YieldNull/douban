from scrapy import Item, Field


class SeedItem(Item):
    mids = Field()


class Movie404Item(Item):
    mid = Field()
    logged_in = Field()


class MovieItem(Item):
    mid = Field()
    subtype = Field()

    poster = Field()

    year = Field()
    title = Field()
    original_title = Field()
    aka = Field()

    directors = Field()
    writers = Field()
    casts = Field()

    genres = Field()
    pubdates = Field()
    duration = Field()
    countries = Field()
    languages = Field()

    summary = Field()
    website = Field()
    douban_site = Field()
    imdb = Field()

    rating = Field()
    rating_count = Field()
    rating_map = Field()

    season = Field()
    episodes_count = Field()
    seasons_count = Field()

    recommendations = Field()


class ActorItem(Item):
    aid = Field()
    mids = Field()
    finished = Field()


class Actor404Item(Item):
    aid = Field()

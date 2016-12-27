from peewee import fn
from scrapy import Request, Spider
from scrapy.exceptions import CloseSpider
from logging import getLogger
from crawler.intermedia import Actor
from crawler.items import ActorItem, Actor404Item

logger = getLogger('ActorSpider')


class ActorSpider(Spider):
    name = 'actor'

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2
    }

    handle_httpstatus_list = [404]

    @classmethod
    def get_dataset(cls):
        return Actor.select().where(Actor.crawled == False).order_by(fn.random())

    def start_requests(self):
        data_set = self.get_dataset()
        logger.info('Dataset count:{:d}'.format(data_set.count()))

        for actor in data_set:
            yield Request(
                url='https://movie.douban.com/celebrity/{:d}/movies?sortby=time&format=text&'.format(actor.aid),
                headers={
                    'Referer': 'https://movie.douban.com/celebrity/{:d}/movies?sortby=time&format=pic&'.format(
                        actor.aid)},
                meta={'aid': actor.aid, 'start': 0}
            )

    def parse(self, response):
        aid = response.meta['aid']
        start = response.meta['start']

        # 404 NOT FOUND
        if response.status in self.handle_httpstatus_list:
            yield Actor404Item(aid=aid)
            raise StopIteration()

        title = response.xpath('/html/head/title')
        if not title:  # IP 被禁，返回一段JS
            raise CloseSpider('IP is restricted')

        total = title.re_first('.*?(\d+).*?')
        if not total:  # 找不到总数
            yield Actor404Item(aid=aid)
            raise StopIteration()

        total = int(total)
        mids = response.selector.re('<a\s+href=".*?movie.douban.com/subject/(\d+)/">')

        logger.info('Got {:d} mids from {:d}. Start:{:d} Amount:{:d}'.format(len(mids), aid, start, total))
        yield ActorItem(mids=mids, aid=aid)

        crawled = start + len(mids)
        if crawled < total:
            yield Request(
                url='https://movie.douban.com/celebrity/{:d}/movies?start={:d}&format=text&sortby=time&'
                    .format(aid, crawled),
                headers={
                    'Referer': 'https://movie.douban.com/celebrity/{:d}/movies?start={:d}&format=text&sortby=time&'
                    .format(aid, start)},
                meta={'aid': aid, 'start': crawled}
            )

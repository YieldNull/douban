from scrapy import Request, Spider
from scrapy.exceptions import CloseSpider
from logging import getLogger
from crawler.intermedia import Actor
from crawler.items import ActorItem

logger = getLogger('ActorSpider')


class ActorSpider(Spider):
    name = 'actor'

    def start_requests(self):
        for actor in Actor.select().where(Actor.crawled == False):
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

        title = response.xpath('/html/head/title')
        if not title:  # IP 被禁，返回一段JS
            raise CloseSpider('IP is restricted')

        total = title.re_first('.*?(\d+).*?')

        # 找不到总数
        if not total:
            yield None
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

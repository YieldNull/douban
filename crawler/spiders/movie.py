import re

from scrapy import Request
from scrapy import Spider

from crawler.items import MovieItem


class MovieSpider(Spider):
    name = 'movie'

    def start_requests(self):
        yield Request(url='https://movie.douban.com/subject/25864085/',
                      headers={
                          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) '
                                        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'},
                      meta={'mid': 25864085})

    def parse(self, response):
        mid = response.meta['mid']

        # 基本信息
        info = response.xpath('//div[@id="info"]')

        title = response.xpath('//*[@id="content"]/h1/span[1]/text()').extract_first()
        names = title.split()

        original_title = None
        if len(names) > 1:
            title = names[0]
            original_title = ' '.join(names[1:])

        year = response.xpath('//*[@id="content"]/h1/span[2]/text()').extract_first()
        year = year.replace('(', '').replace(')', '')

        directors = self._get_actor(info, '导演')
        writers = self._get_actor(info, '编剧')
        casts = self._get_actor(info, '主演')

        genres = info.re('<span property="v:genre">(.*?)</span>')

        countries = info.re_first('<span.*?>制片国家/地区:</span>(.*?)<br/?>')
        if countries:
            countries = [c.strip() for c in countries.strip().split('/')]

        languages = info.re_first('<span.*?>语言:</span>(.*?)<br/?>')
        if languages:
            languages = languages.strip()

        aka = info.re_first('<span.*?>又名:</span>(.*?)<br/?>')
        if aka:
            aka = [name.strip() for name in aka.strip().split('/')]

        pubdates = info.xpath('span[@property="v:initialReleaseDate"]/text()').extract()

        duration = info.xpath('span[@property="v:runtime"]/@content').extract_first()
        if duration:
            subtype = 'movie'
        else:
            duration = info.re_first('<span.*?>单集片长:</span>(.*?)分钟<br/?>').strip()  # 电视剧单集片长
            subtype = 'tv'

        # 以下电视剧独有
        if original_title:
            original_title = re.sub('第.*?季\s+', '', original_title)

        episodes_count = info.re_first('<span.*?>集数:</span>.*?(\d+).*?<br/?>')
        seasons_count = len(info.xpath('select[@id="season"]/option'))
        season = info.xpath('select[@id="season"]/option[@selected="selected"]/text()').extract_first()

        imdb = info.re_first('<a href="http://www.imdb.com/title/(.*?)".*?>.*?</a>')
        website = info.re_first('<span.*?>官方网站:</span>.*?<a.*?href="(.*?)".*?>.*?<br/?>')
        douban_site = info.re_first('<a href=".*?/movieclub/room/(.*?)/".*?>')

        # 简介
        summary = response.xpath('//div[@id="link-report"]/span/text()').extract()
        summary = ''.join([x.strip() for x in summary])

        # 海报
        poster = response.css('#mainpic > a > img').xpath('@src').extract_first()

        # 评价
        rating_info = response.xpath('//div[@id="interest_sectl"]')

        rating = rating_info.xpath('.//strong[@property="v:average"]/text()').extract_first()
        rating_count = rating_info.xpath('.//span[@property="v:votes"]/text()').extract_first()
        rating_map = rating_info.re('<span class="rating_per">(\d+\.\d+)%</span>')

        # 推荐的其它电影
        recommendations = response.xpath('//div[@id="recommendations"]') \
            .xpath('.//dt').re('<a href=".*?movie.douban.com/subject/(.*?)/.*?">')

        item = MovieItem(subtype=subtype, mid=mid, title=title,
                         original_title=original_title, aka=aka, year=int(year),
                         directors=directors, writers=writers, casts=casts, genres=genres,
                         countries=countries, languages=languages, pubdates=pubdates, duration=int(duration),
                         website=website, douban_site=douban_site, imdb=imdb, summary=summary, poster=poster,
                         rating=float(rating), rating_count=int(rating_count), rating_map=rating_map,
                         season=season, seasons_count=seasons_count, episodes_count=episodes_count,
                         recommendations=recommendations)
        yield item

    @staticmethod
    def _get_actor(info, cn_name):
        actors = []
        for link in info.xpath('//span[preceding-sibling::span[text()="{}"]]'.format(cn_name)).xpath('a'):
            aid = link.xpath('@href').re_first('.*?/(\d+)/')
            actor = link.xpath('text()').extract_first()

            actors.append((int(aid), actor))
        return actors

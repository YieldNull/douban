import re
import logging
import datetime
import random

from scrapy import Spider, Request
from scrapy.exceptions import CloseSpider

from crawler.intermedia import Movie
from crawler.items import MovieItem, Movie404Item

logger = logging.getLogger('MovieSpider')


class MovieSpider(Spider):
    """
    电影详情页爬虫
    """

    name = 'movie'
    handle_httpstatus_list = [404, 302]  # 404,302 代表需要登录才能查看。403 在DownloaderMiddleware中处理

    def _get_dataset(self):
        if self.settings.get('LOGIN_ENABLED', False):
            return Movie.select().where(Movie.crawled == False)
        else:
            return Movie.select().where(Movie.crawled == False, Movie.type == Movie.TYPE_NORMAL)

    def start_requests(self):
        """
        从数据库读取没有爬取的影片，进行爬取；并不断循环，直到所有影片都爬完
        爬取过程中并**不要**产生新的Request，而是将其对应的mid存到数据库
        :return:
        """
        year = datetime.datetime.now().year

        data_set = self._get_dataset()

        while data_set.count() > 0:

            logger.info('Dataset count:{:d}'.format(data_set.count()))

            for movie in data_set:
                yield Request(url='https://movie.douban.com/subject/{:d}/?from=tag'.format(movie.mid),
                              headers={'Referer': 'https://www.douban.com/tag/{:d}/?source=topic_search'.format(
                                  random.randint(1888, year))},
                              meta={
                                  'mid': movie.mid,
                                  'login': movie.require_login()},  # 加入login字段，DownloaderMiddleware判断加何种Cookie
                              dont_filter=movie.require_login())  # 不要filter了

            # 还有一部分正在请求，因此会有些重复
            data_set = self._get_dataset()

    def parse(self, response):
        """
        返回 MovieItem 或 Movie404Item，前者表示成功爬取，后者表示需要登录
        :param response:
        :return:
        """
        mid = response.meta['mid']
        logged_in = str(response.meta['login'])

        if response.status in self.handle_httpstatus_list:
            logger.info('HTTP {:d}, Login required. mid: {:d}. logged_in:{:s}'.format(response.status, mid, logged_in))

            if response.status == 302:  # 有些要登录才能访问的页面也是302
                location = response.headers.get('Location', 'None')
                location = str(location, 'utf-8')

                logger.info('Location:{:s}'.format(location))

                # 已登录，被禁，302跳到验证码页面
                if location.find('sorry') > 0:  # https://www.douban.com/misc/sorry?original-url=...
                    yield None
                    raise CloseSpider('IP is restricted')

            # broken link
            yield Movie404Item(mid=mid, logged_in=response.meta['login'])
            raise StopIteration()

        # 基本信息
        info = response.xpath('//div[@id="info"]')

        if not info:
            logger.info('Bad response, logged_in:{:s}. {:s}'.format(logged_in, response.text))
            raise CloseSpider('IP is restricted')  # 停掉

        title = response.xpath('//*[@id="content"]/h1/span[1]/text()').extract_first()
        names = title.split()

        original_title = None
        if len(names) > 1:
            title = names[0]
            original_title = ' '.join(names[1:])

        year = response.xpath('//*[@id="content"]/h1/span[2]/text()').extract_first()

        # 各种各样的year，也是醉了
        if year:
            match = re.search('\(\s*(\d+).*?\)', year)
            if match:
                year = match.group(1)
            else:
                year = -1
        else:
            year = -1

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
            duration = info.re_first('<span.*?>单集片长:</span>.*?(\d+)分钟.*?<br/?>')  # 电视剧单集片长
            duration = duration.strip() if duration else 0
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

        if rating:
            rating_count = rating_info.xpath('.//span[@property="v:votes"]/text()').extract_first()
            rating_map = rating_info.re('<span class="rating_per">(\d+\.\d+)%</span>')
        else:
            rating = 0
            rating_count = 0
            rating_map = [0, 0, 0, 0]

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

        logger.info('Got movie {:s}, mid:{:d}, logged_in:{:s}'.format(title, mid, logged_in))

        yield item

    @staticmethod
    def _get_actor(info, cn_name):
        """
        获取详情页中包含的celebrity信息
        :param info: response.xpath('//div[@id="info"]')
        :param cn_name: 导演？编剧？主演？
        :return: [(aid,actor)...], 有的actor没有对应的链接，则aid=-1
        """
        actors = []
        for link in info.xpath('//span[preceding-sibling::span[text()="{}"]]'.format(cn_name)).xpath('a'):
            aid = link.xpath('@href').re_first('/celebrity/(\d+)/')
            actor = link.xpath('text()').extract_first()

            aid = int(aid) if aid else -1
            actors.append((aid, actor))

        return actors

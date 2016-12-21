# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from crawler.fake import manager

import logging


class DownloaderMiddleware(object):
    def process_request(self, request, spider):
        fake_pair = manager.peek_fake_pair()
        request.meta['fake_pair'] = fake_pair

        request.headers.update({
            'Cookie': fake_pair.cookie,
            'User-Agent': fake_pair.agent
        })

        return None

    def process_response(self, request, response, spider):
        if response.status == 403:
            fake_pair = response.meta['fake_pair']
            manager.pop_fake_pair(fake_pair)

            logging.info(
                '403 Forbidden: Re-Schedule request. '.format(str(fake_pair)))

            return request
        else:
            return response


class DoubanSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # crawler acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

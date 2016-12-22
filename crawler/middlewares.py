# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import traceback

from scrapy import signals
from scrapy.exceptions import IgnoreRequest

from crawler.fake import FakeManager

import logging


class DownloaderMiddleware(object):
    def __init__(self):
        self.manager = FakeManager()

    def process_request(self, request, spider):
        login_enabled = spider.settings.getbool('LOGIN_ENABLED')

        fake_pair = self.manager.peek_fake_pair()
        request.meta['fake_pair'] = fake_pair

        request.headers.update({
            'Cookie': fake_pair.cookie if not login_enabled else spider.settings.get('LOGIN_COOKIE', ''),
            'User-Agent': fake_pair.agent if not login_enabled else spider.settings.get('LOGIN_AGENT', '')
        })

        return None

    def process_response(self, request, response, spider):
        fake_pair = request.meta.pop('fake_pair')

        if response.status == 403:
            if self.manager.pop_fake_pair(fake_pair):
                spider.crawler.engine.close_spider(spider, 'Too many continuous 403 encountered')
                raise IgnoreRequest()
            else:
                logging.info(
                    '403 Forbidden: Re-Schedule request. '.format(str(fake_pair)))

                request = request.copy()
                request.headers.pop('User-Agent')
                request.headers.pop('Cookie')

            return request
        else:
            self.manager.succeed_fake_pair(fake_pair)

            return response

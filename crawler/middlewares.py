from scrapy.exceptions import IgnoreRequest
from crawler.fake import FakeManager

import logging


class DownloaderMiddleware(object):
    """
    为Request添加User-Agent 以及Cookie，管理403
    """

    def __init__(self):
        self.manager = FakeManager()
        self.logger = logging.getLogger('DownloaderMiddleware')

    def process_request(self, request, spider):

        # 伪造Cookie, User-Agent
        fake_pair = self.manager.peek_fake_pair()
        request.meta['fake_pair'] = fake_pair

        # 判断使用伪造的还是已登录账号
        login = request.meta.get('login', False)
        request.headers.update({
            'Cookie': fake_pair.cookie if not login else spider.settings.get('LOGIN_COOKIE', fake_pair.cookie),
            'User-Agent': fake_pair.agent if not login else spider.settings.get('LOGIN_AGENT', fake_pair.cookie)
        })

        return None

    def process_response(self, request, response, spider):
        fake_pair = request.meta.pop('fake_pair')  # 移除fake_pair,因为在spider中用不到

        if response.status == 403:
            if self.manager.pop_fake_pair(fake_pair):  # 连续多次403之后，直接停下来
                spider.crawler.engine.close_spider(spider, 'Too many continuous 403 encountered')
                raise IgnoreRequest()
            else:
                self.logger.info(
                    '403 Forbidden: Re-Schedule request. '.format(str(fake_pair)))

                # 重试, 不会经过查重
                request = request.copy()
                request.headers.pop('User-Agent')
                request.headers.pop('Cookie')  # 复制原有Request对象，移除UA,Cookie,将新对象加入待爬队列

            return request  # 不经过filter
        else:
            self.manager.succeed_fake_pair(fake_pair)  # 持续403 counter清零

            return response

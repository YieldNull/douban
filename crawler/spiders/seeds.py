import re
import datetime
import json
import logging

from scrapy import Request
from scrapy import Spider
from crawler.items import SeedItem

logger = logging.getLogger('SeedSpider')


class SeedSpider(Spider):
    name = 'seed'

    url_tag = 'https://www.douban.com/tag/{tag}/?focus=movie'
    url_api = 'https://www.douban.com/j/tag/items?' \
              'start={start}&limit={limit}&topic_id={tid}&' \
              'topic_name={tag}&mod=movie'

    api_limit = 100

    def start_requests(self):
        for i in range(1888, datetime.datetime.now().year + 1):
            yield Request(self.url_tag.format(tag=i),
                          meta={'tag': i},
                          headers=self._gen_headers({'Referer': 'https://www.douban.com/tag/'}))

    def parse(self, response):
        tag = response.meta['tag']

        m = re.search('topic_id:\s+(\d+)', response.text)

        if m:
            tid = m.group(1)

            logger.info('Got topic id for tag {:d} :{:s}'.format(tag, tid))

            yield self._gen_api_request(tag, tid, 0)
        else:
            js_url = re.search('https://img3\.doubanio\.com/misc/mixed_static/.*?\.js', response.text)

            if js_url:
                yield Request(js_url.group(0), meta={'tag': tag},
                              headers=self._gen_headers({'Referer': self.url_tag.format(tag=tag)}))

    def parse_api(self, response):
        data = json.loads(response.text)
        total = data['total']

        mids = re.findall('<a\s+href="https://movie\.douban\.com/subject/(\d+)/\?from=tag"\s+class="title".*?>',
                          data['html'])

        logger.info('Got {:d} mids from {:s}.'.format(len(mids), response.url))

        yield SeedItem(mids=mids)

        start = response.meta['start']
        if start == 0:
            start += self.api_limit
            while start < total:
                yield self._gen_api_request(response.meta['tag'], response.meta['tid'], start)
                start += self.api_limit

    def _gen_api_request(self, tag, tid, start):

        url = self.url_api.format(start=start, limit=self.api_limit, tag=tag, tid=tid)

        headers = self._gen_headers({
            'Referer': self.url_tag.format(tag=tag),
            'X-Requested-With': 'XMLHttpRequest'})

        meta = {'start': start, 'tag': tag, 'tid': tid}

        return Request(url, meta=meta,
                       headers=headers, callback=self.parse_api)

    def _gen_headers(self, more):
        headers = self.settings.getdict('DEFAULT_REQUEST_HEADERS').copy()
        headers.update(more)

        return headers

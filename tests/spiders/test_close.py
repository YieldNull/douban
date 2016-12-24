from scrapy import Spider, Request
import logging

# close from "parse" in spider
from scrapy.exceptions import CloseSpider


class TestClose(Spider):
    name = 'test_close'

    start_urls = ['http://localhost:5000' for i in range(2000)]

    def parse(self, response):
        logging.info(response.url)

        info = response.xpath('//div[@id="info"]')

        if not info:
            logging.info('Bad response. {:s}'.format(response.text))
            raise CloseSpider('IP is restricted')

        yield None

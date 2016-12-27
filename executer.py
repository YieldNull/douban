import logging
import signal
import sys
import socket
import datetime
import smtplib
from email.mime.text import MIMEText
from pydispatch import dispatcher
from scrapy import signals
from scrapy.settings.default_settings import LOG_FORMAT
from scrapy.crawler import CrawlerRunner
from scrapy.utils import project, log
from twisted.internet import reactor, defer
from crawler.spiders.actor import ActorSpider
from crawler.spiders.movie import MovieSpider, MovieLoginSpider


def send_mail(reason):
    body = "Scrapy has stopped at {:s}. Reason: {:s}.".format(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        reason)

    msg = MIMEText(body)
    msg['Subject'] = "Scrapy Stopped"
    msg['From'] = 'scrapy@scrapy.yieldnull.com'
    msg['To'] = "yieldnull@gmail.com"

    smtp = smtplib.SMTP('localhost')
    smtp.send_message(msg)
    smtp.quit()


class Executor(object):
    def __init__(self, settings, spider_cls_list):
        self.runner = CrawlerRunner(settings)
        self.spider_cls_list = spider_cls_list
        self.logger = logging.getLogger('Executor')
        self.interrupted = False

        dispatcher.connect(self._handle_spider_close, signal=signals.spider_closed)

        signal.signal(signal.SIGTERM, self._handler_sys_signal)
        signal.signal(signal.SIGINT, self._handler_sys_signal)

    @defer.inlineCallbacks
    def _crawl(self):
        while True:
            finished = True

            for spider_cls in self.spider_cls_list:
                if self.interrupted:
                    self.logger.info('interrupted, cancel pending jobs')
                    break

                if spider_cls.get_dataset().count() > 0:
                    finished = False
                    logging.info(
                        'Starting {:s}'.format(spider_cls.__name__))

                    yield self.runner.crawl(spider_cls)

            if finished or self.interrupted:
                break

        reactor.stop()
        self.logger.info('finished')

        if not self.interrupted:
            send_mail('finished')

    def execute(self):
        self._crawl()
        reactor.run(installSignalHandlers=False)

    def _handle_spider_close(self, spider, reason):
        self.logger.info('Spider "{:s}" stopped with reason "{:s}"'.format(spider.name, reason))

        if reason not in ['finished', 'shutdown']:
            self.logger.error('Spider stopped abnormally. Stopping CrawlerRunner')

            self.interrupted = True
            self.runner.stop()

            send_mail(reason)

    def _handler_sys_signal(self, signum, frame):
        self.logger.info('KeyboardInterrupt. Stopping CrawlerRunner')
        self.interrupted = True
        self.runner.stop()


spiders = [MovieSpider, MovieLoginSpider, ActorSpider]


def main():
    # load project settings
    settings = project.get_project_settings()

    # logging to screen
    formatter = logging.Formatter(LOG_FORMAT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    if ''.join(sys.argv).find('INFO') > 0:
        handler.setLevel(logging.INFO)
    else:
        handler.setLevel(logging.DEBUG)

    if socket.gethostname().startswith('YieldNull'):
        logging.getLogger().addHandler(handler)

    # project logging conf
    log.configure_logging(settings)

    # execute
    executor = Executor(settings, spiders)
    executor.execute()


if __name__ == '__main__':
    main()

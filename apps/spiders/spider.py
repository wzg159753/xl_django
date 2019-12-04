from utils.base import http
from utils.base.BaseSpider import BaseSpider


class CompanyListSpider(BaseSpider):
    """
    公司列表爬虫
    """
    def parse(self, resp: object):
        pass

    def crawl(self):
        resp = super().crawl()
        self.parse(resp)


if __name__ == '__main__':
    spider = CompanyListSpider(url='https://www.tianyancha.com/')
    spider.crawl()
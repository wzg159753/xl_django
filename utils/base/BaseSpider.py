from utils.base import http

from utils.get_cookies import get_cookies


class BaseSpider(object):
    """
    基类爬虫
    """
    def __init__(self, url: str, cookie=None, headers=None, *args, **kwargs) -> None:
        self.url = url
        self.headers = headers if headers else http.get_headers()
        self.cookie = cookie if cookie else get_cookies()

    def download(self, url: str, headers: dict) -> object:
        resp = http.download(url=url, headers=headers, method='GET')
        return resp

    def get_xpath(self, xpath: str, response=None, html=None) -> object:
        response = http.get_xpath(xpath, response, html)
        return response

    def crawl(self) -> object:
        resp = self.download(self.url, headers=self.headers)
        return resp

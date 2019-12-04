import random

import requests
from lxml import etree

from xl_django.settings import USER_AGENT_LIST
from utils.get_cookies import get_cookies, get_vip_cookies


def download(url, method='GET', headers=None, proxies=None, cookies=None, data=None):
    """
    下载器
    :param url:
    :param headers:
    :param proxies:
    :param cookies:
    :return:
    """
    if method == 'GET':
        response = requests.get(url, headers=headers, cookies=cookies, proxies=proxies, params=data)
    elif method == 'POST':
        response = requests.post(url, headers=headers, cookies=cookies, proxies=proxies, data=data)
    else:
        response = requests.options(url, headers=headers, cookies=cookies, proxies=proxies, params=data)

    return response


def get_xpath(xpath, response=None, html=None):
    """
    xpath解析模块
    :param xpath:
    :param response:
    :param html:
    :return:
    """
    if response:
        html = etree.HTML(response)
        resp = html.xpath(xpath)
    else:
        resp = html.xpath(xpath)

    return resp


def get_headers(status='ordinary') -> dict:
    """
    获取headers
    :return:
    """
    cookie = ''
    if status == 'ordinary':
        try:
            cookie = get_cookies()
        except Exception as e:
            cookie = get_cookies()
    else:
        try:
            cookie = get_vip_cookies()
        except Exception as e:
            cookie = get_vip_cookies()
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "www.tianyancha.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": random.choice(USER_AGENT_LIST)
    }

    return headers
import redis
import random

import requests
from lxml import etree
from xl_django.settings import ACCOUNT_NUMBERS_LIST

PASSWD = 'uniccc2019'
# HOST = '192.168.1.53'
HOST = '221.214.181.70'


def get_cookies(db=14):
    """
    获取普通cookie
    :param db:
    :return:
    """
    connect = redis.Redis(host=HOST, port=6379, db=db, password=PASSWD)
    keys = connect.keys()
    key = random.choice(keys)
    if key == b'accounts:tianyancha' or key.decode('utf-8') in ACCOUNT_NUMBERS_LIST:
        key = random.choice(keys)
    value = connect.zrange(key, 0, -1)
    cookies = value[0].decode('utf-8')[:-1] if value else ''
    return cookies


def get_fengkong_cookie_key(key, db=14):
    """
    获取vip cookie 和 key
    :param key:
    :param db:
    :return:
    """
    connect = redis.Redis(host=HOST, port=6379, db=db, password=PASSWD)
    value = connect.zrange(key, 0, -1)
    cookies = value[0].decode('utf-8')[:-1] if value else ''
    return key, cookies


def get_cookies_and_key(db=14):
    """
    获取cookie和手机号
    :param db:
    :return:
    """
    connect = redis.Redis(host=HOST, port=6379, db=db, password=PASSWD)
    keys = connect.keys()
    key = random.choice(keys)
    if key == b'accounts:tianyancha':
        key = random.choice(keys)
    key = key.decode('utf-8') if key else ''
    value = connect.zrange(key, 0, -1)
    cookies = value[0].decode('utf-8')[:-1] if value else ''
    return cookies, key


def get_vip_cookies(db=14):
    """
    获取vip cookie
    :param db:
    :return:
    """
    connect = redis.Redis(host=HOST, port=6379, db=db, password=PASSWD)
    key = random.choice(ACCOUNT_NUMBERS_LIST)
    value = connect.zrange(key, 0, -1)
    cookies = value[0].decode('utf-8')[:-1] if value else ''
    return cookies


def get_one_vip_cookie(db=14):
    """
    获取单个vip 账号的cookie
    :param db:
    :return:
    """
    connect = redis.Redis(host=HOST, port=6379, db=db, password=PASSWD)
    value = connect.zrange('13375358581', 0, -1)
    cookies = value[0].decode('utf-8')[:-1] if value else ''
    return cookies


def get_fengkong_vip_cookie(key, db=14):
    """
    获取风险监控的每个vip账号
    :param key:
    :param db:
    :return:
    """
    connect = redis.Redis(host=HOST, port=6379, db=db, password=PASSWD)
    value = connect.zrange(key, 0, -1)
    cookies = value[0].decode('utf-8')[:-1] if value else ''
    return cookies


def get_account_and_vip_cookie(db=14):
    """
    获取账号和vip cookie
    :param db:
    :return:
    """
    connect = redis.Redis(host=HOST, port=6379, db=db, password=PASSWD)
    key = random.choice(ACCOUNT_NUMBERS_LIST)
    value = connect.zrange(key, 0, -1)
    cookies = value[0].decode('utf-8')[:-1] if value else ''
    return key, cookies


def add_companys_id(name, value, db=15):
    """
    向redis添加企业名和企业id
    :param name:
    :param value:
    :param db:
    :return:
    """
    connect = redis.Redis(host=HOST, port=6379, db=db, password=PASSWD)
    status = connect.set(name, value)
    return status


def get_companys_id(name, db=15):
    """
    获取企业对应id
    :param name:
    :param db:
    :return:
    """
    connect = redis.Redis(host=HOST, port=6379, db=db, password=PASSWD)
    value = connect.get(name)
    company_id = value.decode('utf-8') if value else ''
    return company_id


def get_tianyan_id(url, name, headers):
    """
    如果redis没有企业id  就来这搜索然后添加
    :param url:
    :param name:
    :param headers:
    :return:
    """
    response = requests.get(url, headers=headers)
    content = response.text
    soup1 = etree.HTML(content)
    if soup1.xpath(
            '//div[@class="search-item sv-search-company"][1]/div[@class="search-result-single   "]/div[@class="content"]/div[@class="header"]/a/@href'):
        url2 = "".join(soup1.xpath(
            '//div[@class="search-item sv-search-company"][1]/div[@class="search-result-single   "]/div[@class="content"]/div[@class="header"]/a/@href'))
        company_id = url2.split('/')[-1]
        add_companys_id(name, company_id)
        return url2, company_id
    else:
        return 'https://www.tianyancha.com'


def get_monitor_company_number(key, db=13):
    """
    获取监控公司的数量
    :param key:
    :param db:
    :return:
    """
    connect = redis.Redis(host=HOST, port=6379, db=db, password=PASSWD)
    value = connect.hlen(key)
    return value


def add_monitor_company(key, company_id, account, db=13):
    """
    添加账号和公司id到redis
    :param key:
    :param company_id:
    :param account:
    :param db:
    :return:
    """
    connect = redis.Redis(host=HOST, port=6379, db=db, password=PASSWD)
    status = connect.hset(key, company_id, account)
    return status


def get_account(key, db=12):
    """
    获取公司id对应的账号
    :param key:
    :param db:
    :return:
    """
    connect = redis.Redis(host=HOST, port=6379, db=db, password=PASSWD)
    account = connect.get(key)
    return account


def del_key(key, db=12):
    """
    删除12库key
    :param key:
    :param db:
    :return:
    """
    connect = redis.Redis(host=HOST, port=6379, db=db, password=PASSWD)
    status = connect.delete(key)
    return status


def del_hash_key(account, company_id, db=13):
    """
    删除13库的hash
    :param account:
    :param company_id:
    :param db:
    :return:
    """
    connect = redis.Redis(host=HOST, port=6379, db=db, password=PASSWD)
    status = connect.hdel(account, company_id)
    return status

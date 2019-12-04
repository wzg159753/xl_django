import re
import json
import random
import logging
from datetime import datetime

import execjs

from requests.sessions import Session
from requests.cookies import cookiejar_from_dict
from xl_django.settings import USER_AGENT_LIST
from utils.get_cookies import get_account_and_vip_cookie

logger = logging.getLogger('root')


class GetCloud(object):
    """
    股权穿透图，逆向过程
    """
    # 解密返回的数组
    _bb = []
    # 需要拆除拼接的字符串
    a = ",,06btf2,,0zl5whqisecpmu98y,,1,,118oszunvmb9fd7hcpy203j-ilktq46raw5exg,,,0kjrxn-034d1ao7vg,2s6h0pg3nmyldxeakzuf4rb-7oci8v219q,2wtj5,3x70digacthupf6veq4b5kw9s-jly3onzm21r8,4zj3l1us45gch7ot2ka-exybn8i6qp0drvmwf9,,68q-udk7tz4xfvwp2e9om5g1jin63rlbhycas0,5jhpx3d658ktlzb4nrvymga01c9-27qewusfoi,,,7d49moi5kqncs6bjyxlav3tuh-rz207gp8f1we,87-gx65nuqzwtm0hoypifks9lr12v4e8cbadj3,91t8zofl52yq9pgrxesd4nbuamchj3vi0-w7k6"

    def __init__(self):
        # 实例化session
        self.session = Session()
        # 获取cookie 和 手机号，供headers使用
        self.cookie, self.key = self.get_cookie()
        # 设置全局session
        self.session.cookies = cookiejar_from_dict(self.cookie)

    def get_cookie(self):
        """
        获取cookie方法
        :return:
        """
        # 渠道cookie和手机号
        key, cookies = get_account_and_vip_cookie()
        one_cookies = cookies.split(';')
        cookies_tup = [k.split('=') for k in one_cookies]
        # 拼接成cookie
        cookie = {}
        for ck in cookies_tup:
            cookie[ck[0]] = ck[1]

        # 先设置session的全局headers
        self.session.headers = {
            'Host': 'capi.tianyancha.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://dis.tianyancha.com',
            'User-Agent': random.choice(USER_AGENT_LIST),
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Referer': f'https://dis.tianyancha.com/dis/tree?graphId=839023502&origin=https%3A%2F%2Fwww.tianyancha.com&mobile={key}&time=2019-09-17T02:17:39.999Z4-2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

        # 返回cookie和手机号
        return cookie, key

    def _tt(self, e=None, t=None, n=None):
        """
        解密过程tt，判断n是不是空列表，如果是空列表，则添加空列表，如果不是，则添加列表中对应的t
        :param e:
        :param t:
        :param n:
        :return:
        """
        if isinstance(n, list):
            self._bb.append(n)
        else:
            self._bb[int(e)].append(t)

    def func(self, e):
        """
        将字符串分解成字母列表，如果没有则为空
        :param e:
        :return:
        """
        if e:
            t = list(e)
        else:
            t = []
        # print(t)
        if len(t) > 0:
            # print(t)
            # 遍历t列表，取出字符，调用_tt
            for r in range(1, len(t)):
                self._tt(t[0], t[int(r)])
        else:
            self._tt(0, 0, [])

    def default_func(self, e):
        """
        切割混乱字符串a，遍历a，调用func，进一步操作
        :param e:
        :return:
        """
        if str(e) and len(e):
            t = self.a.split(',')
            for i in t:
                self.func(i)

            # 操作完成，_bb是一个列表
            # 取公司id的第一个字符的Unicode字符
            r = ord(e[0])
            # 将所有字符转为列表
            r = list(str(r))
            # 如果列表长度大于一就取第一个位置字符
            if len(r) > 1:
                r = r[1]
            else:
                # 如果小于一就取当前的字符
                r = ''.join(r)

            # 返回_bb列表的对应index列表
            return self._bb[int(r)]

    def get_token(self, res):
        """
        获取通过js解密的token和下次遍历使用的wtf
        :param res:
        :return:
        """
        with open('static/js/get_token.js', 'r') as f:
            result = execjs.compile(f.read())
        data = result.call('get_tokens', res)
        info = re.findall(
            r"!function\(n\){document.cookie='cloud_token=(.*?);path=/;domain=.tianyancha.com;';n.wtf=function\(\){return'(.*?)'}}\(window\);",
            data)[0]
        # 将token和wtf用正则提取
        cloud_token = info[0]
        wtf = info[1]
        # 返回这两个数据
        return cloud_token, wtf

    def get_cloud_utm(self, e, wtf):
        """
        获取cloud_utm加密数据
        :param e:
        :param wtf:
        :return:
        """
        _bb = self.default_func(e)
        c_li = wtf.split(',')
        # c_li = '6,20,17,9,4,17,16,36,33,6,20,27,9,30,34,34,17,22,22,16,15,20,9,36,15,22,20,36,6,4,36,30'
        # c_li = c_li.split(',')
        fxckstr = ''
        # 遍历js返回的wtf取出对应字符，拼接成cloud_utm
        for num in range(len(c_li)):
            fxckstr += _bb[int(c_li[num])]

        return fxckstr

    def run(self, company_id):
        """
        总调度，以及爬虫
        :param company_id:
        :return:
        """
        tt = int(datetime.now().timestamp() * 1000)
        # 在indexnode.js请求之前，需要获取这个请求的v数据，供get_token函数获取cloud_token
        res = self.session.get(
            f'https://capi.tianyancha.com/cloud-equity-provider/v4/qq/name.json?id={company_id}?random={tt}')
        if res.status_code == 200:
            # 获取token和wtf
            cloud_token, wtf = self.get_token(res.json())
            # 将wtf添加到方法中获取cloud_utm
            cloud_utm = self.get_cloud_utm(company_id, wtf)
            logger.info(f'js逆向生成cloud_utm: {cloud_utm}')
            logger.info(f'js逆向生成cloud_token: {cloud_token}')
            # print(cloud_token, cloud_utm)
            # 将参数传入发送股权穿透图的接口请求中
            sed = SendEquityPenetration(self.key, company_id, cloud_token, cloud_utm, self.cookie, self.session)
            result = sed.run()
            # print(result)
            return result


class SendEquityPenetration(object):

    def __init__(self, key, company_id, cloud_token, cloud_utm, cookie, session):
        """
        :param key: 对应账号
        :param company_id: 公司id
        :param cloud_token: cloud_token
        :param cloud_utm: cloud_utm
        :param cookie: 使用的cookie，用于下面headers中的auth_token
        :param session: 上一次的请求session，上一次请求携带的cookie数据，都要在这次请求中使用
        """
        self.key = key
        self.session = session
        self.company_id = company_id
        self.cookie = cookie
        self.cloud_token = cloud_token
        self.cloud_utm = cloud_utm

        self.headers1 = {
            'Host': 'capi.tianyancha.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Mode': 'no-cors',
            'Access-Control-Request-Method': 'GET',
            'Origin': 'https://dis.tianyancha.com',
            'User-Agent': random.choice(USER_AGENT_LIST),  # 随机ua池的ua
            'Access-Control-Request-Headers': 'version,x-auth-token',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-site',
            # 拼接防盗链，对应公司id和cookie账号
            'Referer': f'https://dis.tianyancha.com/dis/tree?graphId={company_id}&origin=https%3A%2F%2Fwww.tianyancha.com&mobile={key}',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

        self.headers2 = {
            'Host': 'capi.tianyancha.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'X-AUTH-TOKEN': self.cookie.get('auth_token'),  # 获取auth_token
            'Origin': 'https://dis.tianyancha.com',
            'User-Agent': random.choice(USER_AGENT_LIST),
            'Sec-Fetch-Mode': 'cors',
            'version': 'TYC-Web',
            'Sec-Fetch-Site': 'same-site',
            'Referer': f'https://dis.tianyancha.com/dis/tree?graphId={company_id}&origin=https%3A%2F%2Fwww.tianyancha.com&mobile={key}',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        # 先将session的headers设置为headers1，用于发起options请求
        self.session.headers = self.headers1

    def request_options(self):
        """
        请求要发两次，第一次是options请求，估计是后端需要先修改cookie，然后再携带页面修改的cookie进行匹配
        :return:
        """
        url = f'https://capi.tianyancha.com/cloud-equity-provider/v4/equity/indexnode.json?id={self.company_id}'
        self.session.options(url)
        # 将session的headers设置为空，重新设置headers2，用于发起拿到数据的get请求
        self.session.headers = {}
        self.session.headers = self.headers2
        cookie = ''
        for key, value in self.cookie.items():
            cookie += f'{key}={value}; '

        # 重新设置逆向出来的cookie
        self.session.cookies.set('cloud_token', self.cloud_token)
        self.session.cookies.set('cloud_utm', self.cloud_utm)

    def request_get(self):
        """
        发送get请求，获取数据
        :return:
        """
        resp = self.session.get(
            f'https://capi.tianyancha.com/cloud-equity-provider/v4/equity/indexnode.json?id={self.company_id}')
        return resp.json()

    def get_cookies_data(self):
        """
        获取cookie，供下一次的节点使用
        :return:
        """
        cookies = self.session.cookies.get_dict()
        cookies['userID'] = self.key
        return cookies

    def run(self):
        """
        总调度，先options再get
        :return:
        """
        self.request_options()
        result = self.request_get()
        cookies = self.get_cookies_data()
        result['cookie'] = cookies
        return result


if __name__ == '__main__':
    get = GetCloud()
    get.run('12562796')

"""
{'domain': '.tianyancha.com', 'expiry': 1568706899, 'httpOnly': False, 'name': '_gat_gtag_UA_123487620_1', 'path': '/', 'secure': False, 'value': '1'}
{'domain': 'www.tianyancha.com', 'httpOnly': True, 'name': 'aliyungf_tc', 'path': '/', 'secure': False, 'value': 'AQAAAJKjp0q7iQEAc9jZG9+HZ1sAupU0'}
{'domain': 'www.tianyancha.com', 'httpOnly': False, 'name': 'csrfToken', 'path': '/', 'secure': True, 'value': 'B-WMzjDFRGckzqSq6Lz16JxX'}
====================================================================================================
{'domain': '.tianyancha.com', 'httpOnly': False, 'name': 'cloud_token', 'path': '/', 'secure': False, 'value': '187cbe23a9754083a6bc5e71bb5a746d'}
{'domain': 'capi.tianyancha.com', 'expiry': 1600251124.972519, 'httpOnly': True, 'name': 'CLOUDID', 'path': '/', 'secure': False, 'value': '7e1c7d1a-2368-409b-a188-5de26f00984e'}
{'domain': '.tianyancha.com', 'expiry': 1568887924.972582, 'httpOnly': False, 'name': 'CT_TYCID', 'path': '/', 'secure': False, 'value': '5a0243ab539a40e786b5690507c1788c'}
{'domain': 'capi.tianyancha.com', 'httpOnly': True, 'name': 'aliyungf_tc', 'path': '/', 'secure': False, 'value': 'AQAAAF0i5C3f2AoAc9jZG2gRdYXz1eNM'}
{'domain': '.tianyancha.com', 'expiry': 1568715725, 'httpOnly': False, 'name': 'cloud_utm', 'path': '/', 'secure': False, 'value': 'b652f7e9df264155ad8cfbeb07a79f87'}
{'domain': '.tianyancha.com', 'expiry': 1568887925.16285, 'httpOnly': False, 'name': 'RTYCID', 'path': '/', 'secure': False, 'value': '304b7739dd6849caab3ee545688c9a6d'}
"""

# 必须字段
"""
_ga   有
ssuid  有
aliyungf_tc  无
Hm_lpvt_e92c8d65d92d534b0fc290df538b4758   有
_gid  有
Hm_lvt_e92c8d65d92d534b0fc290df538b4758   有
undefined  有
bannerFlag  有
CT_TYCID  无  name.json
TYCID  有
RTYCID  无
CLOUDID  无  name.json
"""

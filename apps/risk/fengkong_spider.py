# coding:utf-8
import json
import datetime
import logging

import requests
from lxml import etree

from utils.get_cookies import get_one_vip_cookie

logger = logging.getLogger('root')


class RiskInfo(object):
    dimension = ('主要人员变更', '地址变更', '对外投资', '登记机关变更', '股权变更', '经营异常', '法定代表人变更')
    dimension2 = ('招投标', '被执行人', '失信被执行人', '债券信息')

    def __init__(self, cookie=None):
        cookie = cookie if cookie else self.get_redis_cookies()
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": cookie,  # 获取redis中VIPcookie
            "Host": "www.tianyancha.com",
            "Upgrade-Insecure-Requests": "1",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }

    @staticmethod
    def _get_redis():
        """
        获取redis数据库中cookie
        :return:
        """
        pass

    # 获取vip 风险监控的vip cookie
    def get_redis_cookies(self):
        """
        获取cookie池中的redis
        :return:
        """
        try:
            cookies = get_one_vip_cookie()
        except:
            cookies = get_one_vip_cookie()

        return cookies

    def download(self, url: str):
        """
        下载器
        :param url:
        :return:
        """
        # 没返回text
        return requests.get(url, headers=self.headers)

    def get_xpath(self, xpath: str, response=None, html=None):
        """
        解析
        :param response:
        :return:
        """
        data = None
        if response:
            data_code = etree.HTML(response)
            data = data_code.xpath(xpath)

        if html is not None:
            data = html.xpath(xpath)
        return data

    def get_url_detail(self, url: str):
        # 下载当天监控的最新企业消息
        response = self.download(url)
        # 获取url，当天企业的详情页
        info = self.get_xpath('//div[@data-id="watch_card_d{}"]//a[@class="button -sm"]/@href'.format(
            datetime.datetime.now().strftime('%Y-%m-%d')), response=response.text)
        today = self.get_xpath('//div[@id="_container_watchTimelinePage"]/div[@data-id="watch_card_d{}"]'.format(
            datetime.datetime.now().strftime('%Y-%m-%d')), response=response.text)
        today = today[0] if today else ''
        if today is None:
            logger.info('今日监控动态为空')
            return
        # print(info)
        if not info:
            logger.info('今日无监控动态')
            return

        return info

    def save_txt(self, result, file_name):
        """
        保存文件
        :param result:
        :return:
        """
        with open('E:\\fengkongData\%s.txt' % file_name, 'w', encoding='UTF-8') as f:
            f.write(json.dumps(result))

    def fengkong_util(self, i, **kwargs):
        """
        抽取方法
        :param i:
        :param kwargs:
        :return:
        """
        time = self.get_xpath('.//span[@class="content-date"]/text()', html=i)
        info = self.get_xpath('.//div[@class="content-inner link-warp"]', html=i)
        info_list = []
        for data in info:
            dt = ''.join(self.get_xpath('./text()', html=data)).replace('\xa0', '')
            info_list.append(dt)
        dt_list = []
        for i, j in zip(time, info_list):
            dt_list.append({kwargs.get('key', ''): i, kwargs.get('key2', ''): j})

        return dt_list

    def get_fengkong_data(self, info):
        """
        获取天眼查数据
        :return:
        """
        data_info = []

        for url in info:
            data_code = self.download(url)
            gongsiming = self.get_xpath('//div[@class="header"]/a/text()', response=data_code.text)  # 公司名称
            gongsiming = gongsiming[0] if gongsiming else ''
            tday = self.get_xpath(
                '//div[@id="_container_watchDetailPage"]/div[1]//div[@class="watch-timeline -toggle"]/div',
                response=data_code.text)  # 获取每个公司的tbody  也就是诉讼，专利等
            result = {}
            data_info_list = []
            for i in tday:
                title = self.get_xpath('.//span[@class="title"]//text()', html=i)
                name = title[0] if title else ''
                flav_name = ''.join(title)
                if name in self.dimension2:
                    data = self.fengkong_util(i, key='发布时间', key2='标题')
                    data_info_list.append({flav_name: data})

                elif name in self.dimension:
                    data = self.fengkong_util(i, key='变更日期', key2='变更内容')
                    data_info_list.append({flav_name: data})

                else:
                    ths = self.get_xpath('.//thead//th/text()', html=i)
                    trs = self.get_xpath('.//tbody//tr[@class="watch-tr "] | .//tbody//tr[@class="watch-tr -hide-tr"]',
                                         html=i)
                    dt_list = []
                    for tr in trs:
                        tds = self.get_xpath('./td', html=tr)
                        dic_info = {}
                        for num, td in enumerate(tds):
                            data = self.get_xpath('.//text()', html=td)
                            dic_info[ths[num]] = data[0] if data else ''

                        dt_list.append(dic_info)
                    data_info_list.append({flav_name: dt_list})
            result[gongsiming] = data_info_list
            data_info.append(result)

        return data_info

    def run(self, url, cookie=None):
        """
        控制
        :param url:
        :param cookie:
        :return:
        """
        self.headers.update({'Cookie': cookie})
        # 获取今日详情页中的监控动态
        info = self.get_url_detail(url)
        if not info:
            logger.info('********数据为空*********')
            return
        result = self.get_fengkong_data(info)
        # return json.dumps({'result': result})  # 返回数据
        return result  # 返回数据


if __name__ == '__main__':
    url = 'https://www.tianyancha.com/usercenter/watch'
    risk = RiskInfo()
    risk.run(url)

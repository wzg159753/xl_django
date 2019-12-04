import time
import json
import random
import logging

from django.views import View
from requests.sessions import Session
from requests.cookies import cookiejar_from_dict

from utils.json_func import to_json_data
from .equity_penetration import GetCloud
from utils.res_code import Code, error_map
from xl_django.settings import USER_AGENT_LIST

# Create your views here.


logger = logging.getLogger('root')


class EquityEnetrationBase(View):
    """
    /core/equity_enetration/base
    company_id
    :key
    """

    def get(self, request):
        """
        get请求
        :param request:
        :return:
        """
        start_time = time.time()
        company_id = request.GET.get('company_id')
        if not company_id:
            logger.info('公司id为空')
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA], data={'status': 'No', 'msg': '公司id不能为空'})

        get = GetCloud()
        result = get.run(company_id)
        logger.info(result)
        end_time = time.time()
        logger.info(f'运行时间 - - {end_time - start_time}')
        return to_json_data(errno=Code.OK, errmsg=error_map[Code.OK], data=result)


class EquityEnetrationNext(View):
    """
    /core/equity_enetration/next
    company_id
    :key
    """

    def get(self, request):
        """
        get请求
        :param request:
        :return:
        """
        start_time = time.time()
        session = Session()
        down = request.GET.get('down')
        company_id = request.GET.get('company_id')
        next_id = request.GET.get('next_id')
        holding_company = request.GET.get('holdingCompany', 'true')
        cookies = request.headers.get('Cookie')
        if down and company_id and next_id and cookies:
            cookie = json.loads(cookies)
            headers = {
                'Host': 'capi.tianyancha.com',
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/plain, */*',
                'X-AUTH-TOKEN': cookie.get('auth_token'),  # 获取auth_token
                'Origin': 'https://dis.tianyancha.com',
                'User-Agent': random.choice(USER_AGENT_LIST),
                'Sec-Fetch-Mode': 'cors',
                'version': 'TYC-Web',
                'Sec-Fetch-Site': 'same-site',
                'Referer': f'https://dis.tianyancha.com/dis/tree?graphId={company_id}&origin=https%3A%2F%2Fwww.tianyancha.com&mobile={cookie.get("userID")}',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            }
            url = f'https://capi.tianyancha.com/cloud-equity-provider/v4/equity/nextnode.json?id={next_id}&indexId={company_id}&holdingCompany={holding_company}&direction={down}'
            session.cookies = cookiejar_from_dict(cookie)
            session.headers = headers
            resp = session.get(url)
            logger.info(resp.text)
            end_time = time.time()
            logger.info(f'运行时间 - - {end_time - start_time}')
            return to_json_data(errno=Code.OK, errmsg=error_map[Code.OK], data=json.loads(resp.text))
        return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA], data={'status': 'None', 'msg': '参数设置不全'})

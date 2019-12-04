import json
import logging

from django.views import View

from .fengkong_spider import RiskInfo
from utils.json_func import to_json_data
from utils.res_code import Code, error_map
from xl_django.settings import ACCOUNT_NUMBERS_LIST
from utils.get_cookies import get_fengkong_vip_cookie

# Create your views here.


logger = logging.getLogger('root')


class RiskMonitoring(View):
    """
    /risk/monitor
    """

    def get(self, request):
        url = 'https://www.tianyancha.com/usercenter/watch'
        risk = RiskInfo()
        data = {'result': []}
        for key in ACCOUNT_NUMBERS_LIST:
            cookie = get_fengkong_vip_cookie(key)
            result = risk.run(url, cookie)
            if result:
                data['result'].extend(result)
            else:
                logger.info('风险监控无数据')
        logger.info(f'风险监控数据获取成功: {data}')
        return to_json_data(errno=Code.OK, errmsg=error_map[Code.OK], data=data)

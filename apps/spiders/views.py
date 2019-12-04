import time
import logging

from django.views import View
from django.http import Http404
from utils.json_func import to_json_data
from utils.res_code import Code, error_map
from django.shortcuts import render, redirect, reverse

# Create your views here.

logger = logging.getLogger('root')


class CompanyList(View):
    """
    /company/companylist/new
    search
    pageNum
    base
    :key
    """
    def get(self, request):
        """
        get请求
        :param request:
        :return:
        """
        start_time = time.time()
        org_search = request.GET.get('search')
        search = '/' + org_search if org_search else ''
        page_num = request.GET.get('pageNum', '1')
        key = request.GET.get('key')
        org_base = request.GET.get('base')
        base = '&base=' + org_base if org_base else ''
        org_area_code = request.GET.get('areaCode')
        area_code = '&areaCode=' + org_area_code if org_area_code else ''
        url1 = f'https://www.tianyancha.com/search{search}/p{page_num}?key={key}{base}{area_code}'
        return to_json_data(data={'aaa': 'aaa'})
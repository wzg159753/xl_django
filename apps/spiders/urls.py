from django.urls import path

from . import views


app_name = 'spiders'
urlpatterns = [
    path('companylist/', views.CompanyList.as_view(), name='company_list'),  # 搜索结果页路由
]
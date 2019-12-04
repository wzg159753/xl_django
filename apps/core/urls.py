from django.urls import path

from . import views


app_name = 'core'
urlpatterns = [
    path('equity_enetration/base/', views.EquityEnetrationBase.as_view(), name='equity_enetration_base'),  # 股权穿透
    path('equity_enetration/next/', views.EquityEnetrationNext.as_view(), name='equity_enetration_next'),  # 股权穿透
]
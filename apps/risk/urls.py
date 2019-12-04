from django.urls import path

from . import views


app_name = 'risk'
urlpatterns = [
    path('monitor/', views.RiskMonitoring.as_view(), name='risk_monitor'),  # 风险监控
]
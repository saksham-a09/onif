from django.urls import path
from .views import DashboardView, DepositWalletsView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('overview/', DashboardView.as_view(), name='dashboard_overview'),
    path('deposit-wallets/', DepositWalletsView.as_view(), name='deposit_wallets'),
]

from django.urls import path
from .views import (
    DepositListCreateView, DepositDetailView,
    WithdrawalListCreateView, WithdrawalDetailView,
)

urlpatterns = [
    path('deposits/', DepositListCreateView.as_view(), name='deposit_list_create'),
    path('deposits/<uuid:pk>/', DepositDetailView.as_view(), name='deposit_detail'),
    path('withdrawals/', WithdrawalListCreateView.as_view(), name='withdrawal_list_create'),
    path('withdrawals/<uuid:pk>/', WithdrawalDetailView.as_view(), name='withdrawal_detail'),
]

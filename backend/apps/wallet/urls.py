from django.urls import path
from .views import WalletDetailView, WalletTransactionListView

urlpatterns = [
    path('', WalletDetailView.as_view(), name='wallet_detail'),
    path('transactions/', WalletTransactionListView.as_view(), name='wallet_transactions'),
]

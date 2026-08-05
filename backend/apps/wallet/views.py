from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Wallet, WalletTransaction
from .serializers import WalletSerializer, WalletTransactionSerializer


class WalletDetailView(generics.RetrieveAPIView):
    """GET /api/v1/wallet/ — My wallet balance summary."""
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return wallet


class WalletTransactionListView(generics.ListAPIView):
    """GET /api/v1/wallet/transactions/ — My transaction history, newest first."""
    serializer_class = WalletTransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['transaction_type', 'category']
    search_fields = ['description', 'reference_id']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        try:
            wallet = self.request.user.wallet
            return wallet.transactions.all()
        except Wallet.DoesNotExist:
            return WalletTransaction.objects.none()

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Deposit, Withdrawal
from .serializers import DepositSerializer, WithdrawalSerializer


class DepositListView(generics.ListAPIView):
    """
    GET /api/v1/deposits/ — Admin-only: list all manual deposits.

    User-facing deposits are now embedded in the investment flow.
    Users create investments with deposit proof via POST /api/v1/investments/.
    """
    serializer_class = DepositSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['status', 'network']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        return Deposit.objects.all()


class DepositDetailView(generics.RetrieveAPIView):
    """GET /api/v1/deposits/{id}/ — Admin-only: single deposit detail."""
    serializer_class = DepositSerializer
    permission_classes = [IsAdminUser]
    queryset = Deposit.objects.all()


class WithdrawalListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/withdrawals/ — My withdrawal history.
    POST /api/v1/withdrawals/ — Request a withdrawal from earned wallet balance.
    """
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'withdrawal_type', 'network']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        return self.request.user.withdrawals.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WithdrawalDetailView(generics.RetrieveAPIView):
    """GET /api/v1/withdrawals/{id}/ — Single withdrawal detail."""
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.withdrawals.all()

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Deposit, Withdrawal
from .serializers import DepositSerializer, WithdrawalSerializer


class DepositListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/deposits/ — My deposit history.
    POST /api/v1/deposits/ — Submit a new deposit for admin approval.
    """
    serializer_class = DepositSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'network']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        return self.request.user.deposits.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DepositDetailView(generics.RetrieveAPIView):
    """GET /api/v1/deposits/{id}/ — Single deposit detail."""
    serializer_class = DepositSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.deposits.all()


class WithdrawalListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/withdrawals/ — My withdrawal history.
    POST /api/v1/withdrawals/ — Request a withdrawal.
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

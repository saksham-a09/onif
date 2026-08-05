from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import ReferralCommission
from .serializers import DirectMemberSerializer, ReferralCommissionSerializer

User = get_user_model()


class MyTeamView(generics.ListAPIView):
    """GET /api/v1/referrals/team/ — My direct downline members."""
    serializer_class = DirectMemberSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['email', 'username']
    ordering_fields = ['date_joined']
    ordering = ['-date_joined']

    def get_queryset(self):
        return self.request.user.direct_children.all()


class MyCommissionsView(generics.ListAPIView):
    """GET /api/v1/referrals/commissions/ — My earned commissions."""
    serializer_class = ReferralCommissionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['commission_type', 'is_paid', 'level']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        return self.request.user.commissions.select_related('from_user').all()

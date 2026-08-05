from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Plan, Investment
from .serializers import PlanSerializer, InvestmentSerializer, InvestmentCreateSerializer


class PlanListView(generics.ListAPIView):
    """GET /api/v1/investments/plans/ — List all active investment plans."""
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]
    queryset = Plan.objects.filter(is_active=True)


class InvestmentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/investments/ — My investments (filtered by status).
    POST /api/v1/investments/ — Submit a new investment for admin approval.
    """
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'plan']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InvestmentCreateSerializer
        return InvestmentSerializer

    def get_queryset(self):
        return self.request.user.investments.select_related('plan').all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        investment = serializer.save()
        return Response(
            InvestmentSerializer(investment).data,
            status=status.HTTP_201_CREATED
        )


class InvestmentDetailView(generics.RetrieveAPIView):
    """GET /api/v1/investments/{id}/ — Single investment detail."""
    serializer_class = InvestmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.investments.select_related('plan').all()

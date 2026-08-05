from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Ticket, TicketReply
from .serializers import (
    TicketSerializer, TicketListSerializer,
    TicketReplySerializer, TicketReplyCreateSerializer,
)


class TicketListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/support/tickets/ — My support tickets.
    POST /api/v1/support/tickets/ — Open a new support ticket.
    """
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TicketSerializer
        return TicketListSerializer

    def get_queryset(self):
        return self.request.user.tickets.prefetch_related('replies').all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketDetailView(generics.RetrieveAPIView):
    """GET /api/v1/support/tickets/{id}/ — Ticket detail with all replies."""
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.tickets.prefetch_related('replies__user').all()


class TicketReplyCreateView(APIView):
    """POST /api/v1/support/tickets/{id}/reply/ — Add a reply to a ticket."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk, user=request.user)

        if ticket.status == Ticket.Status.CLOSED:
            return Response(
                {'detail': 'Cannot reply to a closed ticket.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TicketReplyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reply = serializer.save(ticket=ticket, user=request.user)

        # Reopen ticket if it was resolved when user replies
        if ticket.status == Ticket.Status.RESOLVED:
            ticket.status = Ticket.Status.OPEN
            ticket.save(update_fields=['status'])

        return Response(TicketReplySerializer(reply).data, status=status.HTTP_201_CREATED)

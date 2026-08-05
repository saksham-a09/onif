from django.urls import path
from .views import TicketListCreateView, TicketDetailView, TicketReplyCreateView

urlpatterns = [
    path('tickets/', TicketListCreateView.as_view(), name='ticket_list_create'),
    path('tickets/<uuid:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
    path('tickets/<uuid:pk>/reply/', TicketReplyCreateView.as_view(), name='ticket_reply'),
]

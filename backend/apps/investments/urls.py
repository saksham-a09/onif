from django.urls import path
from .views import PlanListView, InvestmentListCreateView, InvestmentDetailView

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='plan_list'),
    path('', InvestmentListCreateView.as_view(), name='investment_list_create'),
    path('<uuid:pk>/', InvestmentDetailView.as_view(), name='investment_detail'),
]

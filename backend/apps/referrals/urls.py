from django.urls import path
from .views import MyTeamView, MyCommissionsView, LevelStatsView

urlpatterns = [
    path('team/', MyTeamView.as_view(), name='referral_team'),
    path('commissions/', MyCommissionsView.as_view(), name='referral_commissions'),
    path('levels/', LevelStatsView.as_view(), name='referral_levels'),
]

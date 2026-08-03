from django.urls import path
from . import leaderboard_views

urlpatterns = [
    path('', leaderboard_views.leaderboard_view, name='leaderboard'),
    path('api/my-rank/', leaderboard_views.my_rank_api, name='my_rank_api'),
]

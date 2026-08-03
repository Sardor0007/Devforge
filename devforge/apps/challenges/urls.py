from django.urls import path
from . import views

urlpatterns = [
    path('', views.challenges_list, name='challenges_list'),
    path('<int:pk>/', views.challenge_detail, name='challenge_detail'),
    path('<int:pk>/join/', views.challenge_join, name='challenge_join'),
    path('my/', views.my_challenges, name='my_challenges'),
    path('<int:pk>/progress/', views.challenge_progress_api, name='challenge_progress_api'),
]

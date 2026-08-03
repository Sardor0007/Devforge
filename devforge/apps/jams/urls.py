# apps/jams/urls.py
from django.urls import path
from . import views

app_name = 'jams'

urlpatterns = [
    path('', views.jam_list, name='list'),
    path('<int:pk>/', views.jam_detail, name='detail'),
    path('create/', views.jam_create, name='create'),
    path('<int:pk>/submit/', views.jam_submit, name='submit'),
    path('<int:pk>/vote/', views.jam_vote, name='vote'),
]

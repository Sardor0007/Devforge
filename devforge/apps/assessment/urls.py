from django.urls import path
from . import views

urlpatterns = [
    path('', views.assessment_list, name='assessment_list'),
    path('<int:pk>/', views.assessment_detail, name='assessment_detail'),
    path('<int:pk>/start/', views.assessment_start, name='assessment_start'),
    path('<int:pk>/submit/', views.assessment_submit, name='assessment_submit'),
    path('<int:pk>/result/', views.assessment_result, name='assessment_result'),
]

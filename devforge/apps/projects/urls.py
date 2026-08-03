from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('projects/', views.project_list_view, name='project_list'),
    path('projects/create/', views.project_create_view, name='project_create'),
    path('projects/<int:pk>/', views.project_detail_view, name='project_detail'),
    path('projects/<int:pk>/apply/', views.project_apply_view, name='project_apply'),
    path('projects/<int:pk>/approve/<int:member_pk>/', views.project_approve_member_view, name='project_approve'),
    path('projects/<int:pk>/tasks/create/', views.task_create_view, name='task_create'),
    path('projects/<int:pk>/tasks/<int:task_pk>/status/', views.task_update_status_view, name='task_status'),
]

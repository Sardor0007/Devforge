from django.urls import path
from . import views

app_name = 'video_lab'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('editor/<int:project_id>/', views.editor_view, name='editor'),
    path('create/', views.create_project, name='create'),
    path('save/<int:project_id>/', views.save_project, name='save'),
    path('upload/<int:project_id>/', views.upload_media, name='upload'),
    path('delete/<int:project_id>/', views.delete_project, name='delete'),
]


from django.urls import path
from . import views

app_name = 'audio_lab'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('editor/<int:project_id>/', views.editor_view, name='editor'),
    path('create/', views.create_project, name='create'),
    path('save/<int:project_id>/', views.save_project, name='save'),
    path('upload/<int:project_id>/', views.upload_audio, name='upload'),
    path('api/ai/<int:project_id>/', views.api_ai_audio, name='api_ai'),
    path('delete/<int:project_id>/', views.delete_project, name='delete'),
    # Legacy
    path('track/create/', views.create_track, name='create_track'),
    path('track/delete/<int:track_id>/', views.delete_track, name='delete_track'),
]

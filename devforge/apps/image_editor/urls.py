from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'image_editor'

router = DefaultRouter()
router.register(r'projects', views.ImageProjectViewSet, basename='project')

urlpatterns = [
    # Template views
    path('', views.dashboard, name='dashboard'),
    path('editor/<int:project_id>/', views.editor_view, name='editor'),
    path('delete/<int:project_id>/', views.delete_project, name='delete'),

    # API endpoints
    path('api/', include(router.urls)),
    path('api/save/<int:project_id>/', views.api_save_project, name='api_save'),
    path('api/upload/<int:project_id>/', views.api_upload_image, name='api_upload'),
    path('api/export/<int:project_id>/', views.api_export_image, name='api_export'),
    path('api/download/<int:project_id>/', views.api_download_image, name='api_download'),
    path('api/create/', views.api_create_project, name='api_create'),
]


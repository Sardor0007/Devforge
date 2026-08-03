from django.urls import path
from . import views

app_name = 'integrations'

urlpatterns = [
    path('feed-to-editor/<int:post_id>/', views.feed_to_editor, name='feed_to_editor'),
    path('asset-to-studio/<int:asset_id>/<int:studio_project_id>/', views.asset_to_studio, name='asset_to_studio'),
    path('showcase-project/<int:project_id>/', views.showcase_project_video, name='showcase_project_video'),
    path('map-to-project/<int:map_id>/<int:project_id>/', views.map_to_project, name='map_to_project'),
]

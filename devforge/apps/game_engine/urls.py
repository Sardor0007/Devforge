from django.urls import path
from . import views, api_views

app_name = 'game_engine'

urlpatterns = [
    # Pages
    path('',                    views.dashboard,    name='dashboard'),
    path('editor/',             views.editor,       name='editor_new'),
    path('editor/<int:pk>/',    views.editor,       name='editor'),
    path('game/<int:pk>/',      views.game_detail,  name='detail'),
    path('play/<int:pk>/',      views.play,         name='play'),

    # API — Project
    path('api/projects/',               api_views.api_create_project,  name='api_create_project'),
    path('api/projects/<int:pk>/',      api_views.api_project_detail,  name='api_project_detail'),
    path('api/projects/<int:pk>/update/', api_views.api_update_project, name='api_update_project'),
    path('api/projects/<int:pk>/delete/', api_views.api_delete_project, name='api_delete_project'),

    # API — Scene
    path('api/projects/<int:pk>/save-scene/',         api_views.api_save_scene,   name='api_save_scene'),
    path('api/projects/<int:pk>/create-scene/',       api_views.api_create_scene, name='api_create_scene'),
    path('api/projects/<int:pk>/scenes/<int:scene_pk>/delete/', api_views.api_delete_scene, name='api_delete_scene'),

    # API — Assets
    path('api/projects/<int:pk>/upload-asset/',              api_views.api_upload_asset, name='api_upload_asset'),
    path('api/projects/<int:pk>/assets/<int:asset_pk>/delete/', api_views.api_delete_asset, name='api_delete_asset'),

    # API — Scripts
    path('api/projects/<int:pk>/save-script/', api_views.api_save_script, name='api_save_script'),

    # API — Build & Publish
    path('api/projects/<int:pk>/build/', api_views.api_build_project, name='api_build'),

    # API — Social
    path('api/projects/<int:pk>/play/',    api_views.api_record_play,  name='api_play'),
    path('api/projects/<int:pk>/like/',    api_views.api_toggle_like,  name='api_like'),
    path('api/projects/<int:pk>/comment/', api_views.api_add_comment,  name='api_comment'),
    path('api/projects/<int:pk>/comments/',api_views.api_comments,     name='api_comments'),
]

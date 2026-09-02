from django.urls import path
from . import views

app_name = "studio_3d"

urlpatterns = [
    path("",                              views.dashboard,    name="dashboard"),
    path("editor/<int:scene_id>/",        views.editor_view,  name="editor"),
    path("create/",                       views.create_scene, name="create"),
    path("save/<int:scene_id>/",          views.save_scene,   name="save"),
    path("delete/<int:scene_id>/",        views.delete_scene, name="delete"),
    path("upload-asset/",                 views.upload_asset, name="upload_asset"),
    path("delete-asset/<int:asset_id>/",  views.delete_asset, name="delete_asset"),
    path("api/assets/",                   views.api_my_assets,name="api_assets"),
]
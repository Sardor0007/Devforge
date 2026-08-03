from django.urls import path
from . import views

app_name = 'studio'

urlpatterns = [
    path('', views.project_list, name='index'),
    path('create/', views.create_project, name='create_project'),
    path('delete/<int:project_id>/', views.delete_project, name='delete_project'),
    path('editor/<int:project_id>/', views.editor_view, name='editor'),
    path('save/<int:project_id>/', views.save_project, name='save_project'),
]

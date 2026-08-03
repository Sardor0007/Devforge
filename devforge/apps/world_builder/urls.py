from django.urls import path
from . import views

app_name = 'world_builder'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('editor/<int:map_id>/', views.editor_view, name='editor'),
    
    # Short names for frontend templates
    path('create/', views.create_map, name='create'),
    path('save/<int:map_id>/', views.save_map, name='save'),
    path('delete/<int:map_id>/', views.delete_map, name='delete'),
    path('rename/<int:map_id>/', views.rename_map, name='rename'),
    
    # Original/verbose names for test cases and compatibility
    path('create/', views.create_map, name='create_map'),
    path('save/<int:map_id>/', views.save_map, name='save_map'),
    path('delete/<int:map_id>/', views.delete_map, name='delete_map'),
    path('rename/<int:map_id>/', views.rename_map, name='rename_map'),
]

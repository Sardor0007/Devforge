from django.urls import path
from . import views

urlpatterns = [
    path('',                          views.analytics_dashboard,   name='analytics_dashboard'),
    path('api/',                      views.analytics_api,         name='analytics_api'),
    path('users/',                    views.user_management,       name='user_management'),
    path('users/<int:pk>/toggle/',    views.toggle_user_active,    name='user_toggle_active'),
    path('users/<int:pk>/verify/',    views.toggle_user_verified,  name='user_toggle_verified'),
    path('users/<int:pk>/subscription/', views.update_user_subscription, name='admin_update_subscription'),
    path('users/<int:pk>/balance/',    views.update_user_balance,      name='admin_update_balance'),
    path('projects/',                 views.project_management,    name='admin_projects'),
]

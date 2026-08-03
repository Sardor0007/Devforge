from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_list_view, name='service_list'),
    path('create/', views.service_create_view, name='service_create'),
    path('<int:pk>/', views.service_detail_view, name='service_detail'),
    path('<int:pk>/order/', views.order_create_view, name='order_create'),
    path('<int:pk>/review/', views.review_create_view, name='review_create'),
    path('orders/', views.order_list_view, name='order_list'),
    path('orders/<int:pk>/confirm/', views.order_confirm_view, name='order_confirm'),
]

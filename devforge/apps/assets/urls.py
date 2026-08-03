from django.urls import path
from . import views

urlpatterns = [
    path('', views.asset_list_view, name='asset_list'),
    path('upload/', views.asset_upload_view, name='asset_upload'),
    path('cart/', views.cart_list_view, name='cart_list'),
    path('cart/add/<int:pk>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/checkout/', views.checkout_view, name='checkout'),
    path('api/cart/count/', views.cart_count_api, name='cart_count_api'),
    path('<int:pk>/', views.asset_detail_view, name='asset_detail'),
    path('<int:pk>/like/', views.asset_like_view, name='asset_like'),
    path('<int:pk>/download/', views.asset_download_view, name='asset_download'),
    path('<int:pk>/buy/', views.asset_buy_direct, name='asset_buy_direct'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('',                             views.feed_view,          name='feed'),
    path('post/create/',                 views.post_create_view,   name='post_create'),
    path('post/<int:pk>/',               views.post_detail_view,   name='post_detail'),
    path('post/<int:pk>/like/',          views.post_like_view,     name='post_like'),
    path('post/<int:pk>/comment/',       views.comment_add_view,   name='comment_add'),
    path('post/<int:pk>/delete/',        views.post_delete_view,   name='post_delete'),
    path('follow/<str:username>/',       views.follow_toggle_view, name='follow_toggle'),
    path('user/<str:username>/',         views.user_feed_view,     name='user_feed'),
]

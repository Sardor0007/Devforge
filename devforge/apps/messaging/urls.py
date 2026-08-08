from django.urls import path
from . import views

urlpatterns = [
    path('',                           views.inbox_view,              name='inbox'),
    path('<int:conv_id>/',             views.conversation_view,       name='conversation'),
    path('<int:conv_id>/send/',        views.send_message_view,       name='send_message'),
    path('<int:conv_id>/poll/',        views.poll_messages_view,      name='poll_messages'),
    path('start/<str:username>/',      views.start_conversation_view, name='start_conversation'),
    path('api/unread/',                views.unread_count_api,        name='messages_unread_api'),
    path('api/search/',                views.user_search_api,         name='messages_user_search'),
]

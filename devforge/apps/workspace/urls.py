from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/',                              views.workspace_view,       name='workspace'),
    path('file/create/<int:workspace_pk>/',        views.file_create_view,     name='file_create'),
    path('file/<int:file_pk>/save/',               views.file_save_view,       name='file_save'),
    path('file/<int:file_pk>/load/',               views.file_load_view,       name='file_load'),
    path('file/<int:file_pk>/raw/',                views.file_raw_view,        name='file_raw'),
    path('file/<int:file_pk>/delete/',             views.file_delete_view,     name='file_delete'),
    path('file/<int:file_pk>/rename/',             views.file_rename_view,     name='file_rename'),
    path('folder/create/<int:workspace_pk>/',      views.folder_create_view,   name='folder_create'),
    path('tree/<int:workspace_pk>/',               views.file_tree_view,       name='file_tree'),
    path('upload/<int:workspace_pk>/',             views.file_upload_view,     name='file_upload'),
    path('github/repos/',                          views.github_repos_view,    name='github_repos'),
    path('github/tree/',                           views.github_tree_view,     name='github_tree'),
    path('github/import/<int:workspace_pk>/',      views.github_import_view,   name='github_import'),
    path('chat/<int:room_pk>/send/',               views.chat_message_view,    name='chat_send'),
    path('chat/<int:room_pk>/messages/',           views.chat_messages_view,   name='chat_messages'),
    path('terminal/<int:workspace_pk>/run/',       views.terminal_run_view,    name='terminal_run'),
    path('terminal/<int:workspace_pk>/cwd/',       views.terminal_cwd_view,    name='terminal_cwd'),
    path('terminal/<int:workspace_pk>/input/',     views.terminal_input_view,  name='terminal_input'),
    path('terminal/<int:workspace_pk>/poll/',      views.terminal_poll_view,   name='terminal_poll'),
    path('terminal/<int:workspace_pk>/stop/',      views.terminal_stop_view,   name='terminal_stop'),
    path('package-install/<int:workspace_pk>/',    views.package_install_view, name='package_install'),
]

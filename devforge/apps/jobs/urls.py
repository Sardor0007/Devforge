from django.urls import path
from . import views

urlpatterns = [
    path('',                               views.job_list_view,          name='job_list'),
    path('create/',                        views.job_create_view,        name='job_create'),
    path('<int:pk>/',                      views.job_detail_view,        name='job_detail'),
    path('<int:pk>/proposal/',             views.proposal_create_view,   name='proposal_create'),
    path('proposal/<int:prop_pk>/accept/', views.proposal_accept_view,   name='proposal_accept'),
    path('<int:pk>/fund/',                 views.escrow_fund_view,       name='escrow_fund'),
    path('my-jobs/',                       views.my_jobs_view,           name='my_jobs'),
    path('my-applications/',               views.my_applications_view,   name='my_applications'),
    path('<int:pk>/deliver/',              views.delivery_submit_view,   name='delivery_submit'),
    path('<int:pk>/approve/',              views.delivery_approve_view,   name='delivery_approve'),
    path('<int:pk>/dispute/',              views.dispute_open_view,       name='dispute_open'),
]

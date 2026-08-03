from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('course/<slug:course_slug>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('create-course/', views.create_course, name='create_course'),
    path('course/<slug:slug>/add-lesson/', views.add_lesson, name='add_lesson'),
    path('lesson/<int:lesson_id>/comment/', views.add_comment, name='add_comment'),
    path('my-courses/', views.my_courses, name='my_courses'),
]

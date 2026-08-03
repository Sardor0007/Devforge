try:
    from rest_framework.routers import DefaultRouter
except ImportError:
    raise ImportError("djangorestframework o'rnatilmagan.")

from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'tags',     views.TagViewSet,     basename='api-tags')
router.register(r'users',    views.UserViewSet,    basename='api-users')
router.register(r'projects', views.ProjectViewSet, basename='api-projects')
router.register(r'posts',    views.PostViewSet,    basename='api-posts')
router.register(r'jobs',     views.JobViewSet,     basename='api-jobs')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),   # Session auth uchun
]

"""
DevForge REST API - URL Router v2
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

router = DefaultRouter()
router.register(r"tags",          views.TagViewSet,          basename="api-tags")
router.register(r"users",         views.UserViewSet,         basename="api-users")
router.register(r"projects",      views.ProjectViewSet,      basename="api-projects")
router.register(r"posts",         views.PostViewSet,         basename="api-posts")
router.register(r"jobs",          views.JobViewSet,          basename="api-jobs")
router.register(r"assets",        views.AssetViewSet,        basename="api-assets")
router.register(r"notifications", views.NotificationViewSet, basename="api-notifications")
router.register(r"messages",      views.ConversationViewSet, basename="api-messages")

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────
    path("auth/register/",       views.RegisterView.as_view(),      name="api-register"),
    path("auth/login/",          views.LoginView.as_view(),         name="api-login"),
    path("auth/token/",          TokenObtainPairView.as_view(),     name="token_obtain_pair"),
    path("auth/token/refresh/",  TokenRefreshView.as_view(),        name="token_refresh"),
    path("auth/token/verify/",   TokenVerifyView.as_view(),         name="token_verify"),
    path("auth/password/change/",views.ChangePasswordView.as_view(),name="api-change-password"),

    # ── Viewsets ──────────────────────────────────────────────────────────
    path("", include(router.urls)),
]
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts import views as auth_views
from apps.accounts import dashboard_views as accounts_dash
from apps import ai_views
from django.views.generic import RedirectView, TemplateView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.home_view, name='home'),
    path('manifest.json', TemplateView.as_view(template_name='manifest.json', content_type='application/json'), name='manifest_json'),
    path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/javascript'), name='sw_js'),
    path('auth/', include('apps.accounts.urls')),
    path('dashboard/', accounts_dash.smart_dashboard, name='dashboard'),
    path('super-admin/', accounts_dash.super_admin_dashboard, name='super_admin_dashboard'),
    path('super-admin/toggle-all-studios/', accounts_dash.super_admin_toggle_all_studios, name='super_admin_toggle_all_studios'),
    path('super-admin/delete-project/<int:pk>/', accounts_dash.super_admin_delete_project, name='super_admin_delete_project'),
    path('super-admin/approve-asset/<int:pk>/', accounts_dash.super_admin_approve_asset, name='super_admin_approve_asset'),
    path('super-admin/delete-post/<int:pk>/', accounts_dash.super_admin_delete_post, name='super_admin_delete_post'),
    path('super-admin/verify-user/<int:pk>/', accounts_dash.super_admin_toggle_verify_user, name='super_admin_toggle_verify_user'),
    path('super-admin/change-subscription/<int:pk>/', accounts_dash.admin_change_subscription, name='admin_change_subscription'),
    path('super-admin/adjust-wallet/<int:pk>/', accounts_dash.admin_adjust_wallet, name='admin_adjust_wallet'),
    path('projects/', include('apps.projects.urls')),
    path('assets/', include('apps.assets.urls')),
    path('marketplace/', include('apps.marketplace.urls')),
    path('workspace/', include('apps.workspace.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('messages/', include('apps.messaging.urls')),
    path('feed/', include('apps.feed.urls')),
    path('jobs/', include('apps.jobs.urls')),
    path('learn/', include('apps.learn.urls')),
    path('assessment/', include('apps.assessment.urls')),
    path('challenges/', include('apps.challenges.urls')),
    path('jams/', include('apps.jams.urls')),
    path('leaderboard/', include('apps.accounts.leaderboard_urls')),
    path('studio/', include('apps.studio.urls')),
    path('studio/integrations/', include('apps.integrations.urls')),
    path('studio/image-editor/', include('apps.image_editor.urls')),
    path('studio/audio-lab/', include('apps.audio_lab.urls')),
    path('studio/video-lab/', include('apps.video_lab.urls')),
    path('studio/world-builder/', include('apps.world_builder.urls')),
    path('studio/3d-studio/', include('apps.studio_3d.urls')),
    path('game-engine/', include('apps.game_engine.urls')),
    path('github/', include([
        path('sync/', __import__('apps.accounts.github_views', fromlist=['github_sync_repos']).github_sync_repos, name='github_sync_repos'),
        path('import/<str:repo_name>/', __import__('apps.accounts.github_views', fromlist=['github_import_repo']).github_import_repo, name='github_import_repo'),
        path('repos-api/', __import__('apps.accounts.github_views', fromlist=['github_repos_api']).github_repos_api, name='github_repos_api'),
    ])),
    path('api/v1/', include('apps.api.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('accounts/', include('allauth.urls')),  # Google + GitHub OAuth
    path('search/', __import__('apps.search_views', fromlist=['global_search_view']).global_search_view, name='search'),
    path('search/suggestions/', __import__('apps.search_views', fromlist=['search_suggestions_api']).search_suggestions_api, name='search_suggestions'),
    # AI endpoints
    path('ai/generate-tasks/',       ai_views.ai_generate_tasks,       name='ai_generate_tasks'),
    path('ai/generate-description/', ai_views.ai_generate_description,  name='ai_generate_description'),
    path('ai/generate-job-desc/',    ai_views.ai_generate_job_desc,     name='ai_generate_job_desc'),
    path('ai/explain-code/',         ai_views.ai_explain_code,          name='ai_explain_code'),
    path('ai/format-code/',          ai_views.ai_format_code,           name='ai_format_code'),
    path('ai/debug-code/',           ai_views.ai_debug_code,            name='ai_debug_code'),
    path('payments/',                 include('apps.payments.urls')),
    
    # Strategic Hubs
    path('gamelab/', __import__('apps.strategic_views', fromlist=['gamelab_view']).gamelab_view, name='gamelab'),
    path('publisher-hub/', __import__('apps.strategic_views', fromlist=['publisher_hub_view']).publisher_hub_view, name='publisher_hub'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


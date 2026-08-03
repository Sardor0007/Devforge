from django.urls import path
from . import views
from . import onboarding_views

urlpatterns = [
    path('onboarding/', onboarding_views.onboarding_view, name='onboarding'),
    path('onboarding/complete-tour/', onboarding_views.complete_tour_api, name='complete_tour_api'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('skill/add/', views.skill_add_view, name='skill_add'),
    path('skill/delete/<int:pk>/', views.skill_delete_view, name='skill_delete'),
    path('portfolio/add/', views.portfolio_add_view, name='portfolio_add'),
    # Parolni tiklash
    path('password-reset/', views.password_reset_request_view, name='password_reset'),
    path('password-reset/done/', views.password_reset_done_view, name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    # Email tasdiqlash
    path('verify-email/<uidb64>/<token>/', views.verify_email_view, name='verify_email'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),
    # Obuna va Balans
    path('subscriptions/', views.subscription_plans, name='subscription_plans'),
    path('subscriptions/upgrade/<str:plan_type>/', views.upgrade_subscription, name='upgrade_subscription'),
    path('balance/top-up/', views.top_up_balance, name='top_up_balance'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('wallet/withdraw/', views.withdraw_view, name='wallet_withdraw'),
    path('wallet/transfer-to-deposit/', views.transfer_to_deposit_view, name='wallet_transfer'),
]

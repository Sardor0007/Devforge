from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Wallet (deposit)
    path('deposit/',                views.deposit_view,                 name='deposit'),
    path('success/',                views.deposit_success_view,         name='deposit_success'),
    path('cancel/',                 views.deposit_cancel_view,          name='deposit_cancel'),
    path('api/balance/',            views.wallet_api,                   name='wallet_api'),

    # Subscription
    path('plans/',                  views.subscription_plans_view,      name='plans'),
    path('subscribe/<str:plan>/',   views.subscription_checkout_view,   name='subscribe'),
    path('subscription-success/',   views.subscription_success_view,    name='subscription_success'),
    path('subscription-cancel/',    views.subscription_cancel_view,     name='subscription_cancel'),

    # Eski URLs (backward compat)
    path('subscription/<str:plan>/', views.subscription_checkout_view,  name='subscription'),

    # Stripe Webhook (3-qatlam)
    path('stripe/webhook/',         views.stripe_webhook_view,          name='stripe_webhook'),
    path('webhook/',                views.stripe_webhook_view,          name='webhook'),
]

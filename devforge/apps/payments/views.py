"""
DevForge — Stripe Payment Integration (6-qatlam arxitektura)

Qatlam 1: Foydalanuvchi — Wallet, Subscription, Tournament
Qatlam 2: Stripe — barcha to'lovlar USD da
Qatlam 3: Django Webhook — checkout.completed | invoice.paid | transfer.created
Qatlam 4: Models — Transaction, UserBalance, Subscription
Qatlam 5: Rejalar — Free $0 | Pro $9/oy | Studio $25/oy | Enterprise custom
Qatlam 6: Marketplace + Tournament — Stripe Connect (seller payout, prize pool)
"""
import json
import logging
from decimal import Decimal
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)


# ── STRIPE HELPER ─────────────────────────────────────────────────────────────

def _get_stripe():
    """Stripe moduli va kalitini tekshirish"""
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return stripe
    except ImportError:
        return None


def _get_or_create_stripe_customer(stripe, user):
    """Stripe Customer ID olish yoki yaratish"""
    if user.stripe_customer_id:
        try:
            return stripe.Customer.retrieve(user.stripe_customer_id)
        except Exception:
            pass
    customer = stripe.Customer.create(
        email=user.email,
        name=user.get_full_name() or user.username,
        metadata={'user_id': str(user.pk)},
    )
    user.stripe_customer_id = customer.id
    user.save(update_fields=['stripe_customer_id'])
    return customer


# ── NARX REJALAR (5-qatlam) ──────────────────────────────────────────────────

PLAN_PRICES = {
    'pro':    {
        'amount':       900,       # $9.00 (cents)
        'amount_usd':   Decimal('9.00'),
        'name':         'Pro — $9/oy',
        'description':  '10 ta fayl, barcha ijodiy vositalar',
        'color':        '#6366f1',
        'features':     ['10 fayl/oy', '3D Studio', 'Workspace', 'Marketplace', 'Priority support'],
    },
    'studio': {
        'amount':       2500,      # $25.00
        'amount_usd':   Decimal('25.00'),
        'name':         'Studio — $25/oy',
        'description':  'Studio + Tournament + 50 fayl + Analytics',
        'color':        '#9333ea',
        'features':     ['50 fayl/oy', 'Hamma Pro imkoniyatlar', 'Tournament yaratish', 'Advanced analytics', 'Team workspace'],
    },
    'enterprise': {
        'amount':       None,      # Custom
        'amount_usd':   None,
        'name':         'Enterprise — Custom',
        'description':  'Katta jamoalar uchun maxsus narx',
        'color':        '#0ea5e9',
        'features':     ['Cheksiz fayl', 'Dedicated support', 'Custom integrations', 'SLA kafolat', 'White-label'],
    },
}

DEPOSIT_OPTIONS = [5, 10, 25, 50, 100, 250]  # USD


# ── DEPOSIT (WALLET) VIEWS ────────────────────────────────────────────────────

@login_required
def deposit_view(request):
    """Stripe Checkout orqali wallet'ga USD qo'shish"""
    stripe = _get_stripe()
    # UserBalance olish yoki yaratish
    from apps.accounts.models import UserBalance
    wallet, _ = UserBalance.objects.get_or_create(user=request.user)

    context = {
        'deposit_options': DEPOSIT_OPTIONS,
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
        'stripe_available': bool(stripe and getattr(settings, 'STRIPE_SECRET_KEY', '')),
        'wallet': wallet,
        'balance': wallet.deposit_balance,
        'deposit': wallet.deposit_balance,
        'earnings': wallet.earnings_balance,
    }

    if request.method == 'POST':
        if not stripe or not getattr(settings, 'STRIPE_SECRET_KEY', ''):
            messages.error(request, "To'lov tizimi hozircha mavjud emas.")
            return render(request, 'payments/deposit.html', context)

        try:
            amount_usd = int(request.POST.get('amount', 10))
            if amount_usd not in DEPOSIT_OPTIONS:
                amount_usd = 10

            customer = _get_or_create_stripe_customer(stripe, request.user)
            session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'DevForge Wallet — ${amount_usd}',
                            'description': 'DevForge platformasidagi hamyon balansi',
                        },
                        'unit_amount': amount_usd * 100,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/payments/success/') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri('/payments/cancel/'),
                metadata={
                    'user_id':    str(request.user.pk),
                    'amount_usd': str(amount_usd),
                    'type':       'wallet_deposit',
                },
            )
            return redirect(session.url, code=303)

        except Exception as e:
            logger.error(f"Stripe deposit error for user {request.user.pk}: {e}")
            messages.error(request, f"To'lov xatosi: {e}")

    return render(request, 'payments/deposit.html', context)


@login_required
def deposit_success_view(request):
    """Muvaffaqiyatli wallet to'lovidan keyin"""
    session_id = request.GET.get('session_id', '')
    context = {'session_id': session_id}

    if session_id:
        stripe = _get_stripe()
        if stripe and getattr(settings, 'STRIPE_SECRET_KEY', ''):
            try:
                session = stripe.checkout.Session.retrieve(session_id)
                context['amount_usd'] = Decimal(str(session.amount_total / 100))
            except Exception as e:
                logger.warning(f"Could not retrieve session {session_id}: {e}")

    messages.success(request, "✅ To'lov muvaffaqiyatli! Balans yangilandi.")
    return render(request, 'payments/success.html', context)


@login_required
def deposit_cancel_view(request):
    messages.warning(request, "To'lov bekor qilindi.")
    return render(request, 'payments/cancel.html')


# ── SUBSCRIPTION VIEWS (5-qatlam) ─────────────────────────────────────────────

@login_required
def subscription_plans_view(request):
    """Barcha obuna rejalari"""
    from apps.accounts.models import Subscription
    try:
        current_sub = request.user.subscription
    except Subscription.DoesNotExist:
        current_sub = None

    return render(request, 'payments/plans.html', {
        'plans': PLAN_PRICES,
        'current_sub': current_sub,
        'current_plan': request.user.subscription_type,
    })


@login_required
def subscription_checkout_view(request, plan):
    """Stripe Checkout orqali obuna to'lovi"""
    stripe = _get_stripe()

    if plan not in PLAN_PRICES or PLAN_PRICES[plan]['amount'] is None:
        # Enterprise — sales jamoasi bilan bog'lanish
        messages.info(request, "Enterprise tarifi uchun sales@devforge.uz ga murojaat qiling.")
        return redirect('payments:plans')

    plan_data = PLAN_PRICES[plan]
    context = {
        'plan': plan,
        'plan_data': plan_data,
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
        'stripe_available': bool(stripe and getattr(settings, 'STRIPE_SECRET_KEY', '')),
    }

    if request.method == 'POST':
        if not stripe or not getattr(settings, 'STRIPE_SECRET_KEY', ''):
            messages.error(request, "To'lov tizimi hozircha mavjud emas.")
            return render(request, 'payments/subscription.html', context)

        try:
            customer = _get_or_create_stripe_customer(stripe, request.user)
            session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': plan_data['name']},
                        'unit_amount': plan_data['amount'],
                        'recurring': {'interval': 'month'},
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=request.build_absolute_uri('/payments/subscription-success/') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri('/payments/cancel/'),
                metadata={
                    'user_id': str(request.user.pk),
                    'type':    'subscription',
                    'plan':    plan,
                },
            )
            return redirect(session.url, code=303)

        except Exception as e:
            logger.error(f"Stripe subscription error user={request.user.pk} plan={plan}: {e}")
            messages.error(request, f"To'lov xatosi: {e}")

    return render(request, 'payments/subscription.html', context)


@login_required
def subscription_success_view(request):
    messages.success(request, "✅ Obuna muvaffaqiyatli faollashtirildi!")
    return render(request, 'payments/subscription_success.html', {
        'current_plan': request.user.subscription_type,
    })


@login_required
def subscription_manage_view(request):
    """Obuna boshqaruv paneli — hozirgi reja, foydalanish statistikasi, hisob-faktura tarixi."""
    from apps.accounts.models import Subscription
    try:
        current_sub = request.user.subscription
    except Exception:
        current_sub = None

    # Hisob-fakturalar (Transaction modeldan)
    from apps.accounts.models import Transaction
    invoices = Transaction.objects.filter(
        user=request.user,
        transaction_type__in=['subscription', 'deposit']
    ).order_by('-created_at')[:12]

    return render(request, 'payments/subscription.html', {
        'current_sub': current_sub,
        'current_plan': request.user.subscription_type,
        'invoices': invoices,
        'plans': PLAN_PRICES,
    })


@login_required
def subscription_cancel_view(request):
    """Obunani bekor qilish"""
    from apps.accounts.models import Subscription
    try:
        sub = request.user.subscription
        stripe = _get_stripe()
        if stripe and sub.stripe_subscription_id:
            stripe.Subscription.cancel(sub.stripe_subscription_id)
        sub.cancel()
        messages.success(request, "Obuna bekor qilindi. Muddat tugaguncha foydalana olasiz.")
    except Subscription.DoesNotExist:
        messages.error(request, "Faol obuna topilmadi.")
    return redirect('payments:plans')


# ── STRIPE WEBHOOK (3-qatlam) ─────────────────────────────────────────────────

@csrf_exempt
@require_POST
def stripe_webhook_view(request):
    """
    Stripe webhook — 3 ta handler:
      checkout.session.completed → wallet deposit yoki subscription ticket
      invoice.paid               → oylik obuna yangilanishi
      customer.subscription.*    → subscription holat o'zgarishi
    CSRF exempt: Stripe Signature bilan himoyalangan.
    """
    stripe = _get_stripe()
    if not stripe:
        return HttpResponse("Stripe not configured", status=503)

    payload       = request.body
    sig_header    = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        logger.warning("Stripe webhook: invalid payload")
        return HttpResponse("Invalid payload", status=400)
    except stripe.error.SignatureVerificationError:
        logger.warning("Stripe webhook: invalid signature")
        return HttpResponse("Invalid signature", status=400)

    event_type = event['type']
    data_obj   = event['data']['object']
    logger.info(f"Stripe webhook: {event_type}")

    # 3-qatlam: 3 xil handler
    if event_type == 'checkout.session.completed':
        _handle_checkout_completed(data_obj)

    elif event_type == 'invoice.paid':
        _handle_invoice_paid(data_obj)

    elif event_type in ('customer.subscription.updated', 'customer.subscription.deleted'):
        _handle_subscription_changed(data_obj, event_type)

    elif event_type == 'transfer.created':
        _handle_transfer_created(data_obj)

    return HttpResponse(status=200)


def _get_user_by_customer(stripe_customer_id):
    """Stripe customer_id bo'yicha foydalanuvchi topish"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        return User.objects.get(stripe_customer_id=stripe_customer_id)
    except User.DoesNotExist:
        logger.error(f"No user found for stripe_customer_id={stripe_customer_id}")
        return None


def _handle_checkout_completed(session):
    """
    checkout.session.completed → wallet deposit yoki subscription ticket
    """
    from django.contrib.auth import get_user_model
    from apps.accounts.models import UserBalance, Subscription
    User = get_user_model()

    metadata     = session.get('metadata', {})
    user_id      = metadata.get('user_id')
    payment_type = metadata.get('type', 'wallet_deposit')

    if not user_id:
        logger.warning("Stripe checkout.completed: no user_id in metadata")
        return

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return

    if payment_type == 'wallet_deposit':
        amount_cents = session.get('amount_total', 0)
        amount_usd   = Decimal(str(amount_cents / 100))
        payment_intent = session.get('payment_intent', '')

        wallet, _ = UserBalance.objects.get_or_create(user=user)
        wallet.credit(amount_usd, description=f"Stripe wallet deposit ${amount_usd}", payment_intent=payment_intent)
        logger.info(f"Wallet +${amount_usd} for user #{user.pk}")

    elif payment_type == 'subscription':
        plan = metadata.get('plan', 'pro')
        # Subscription obyekti yangilash
        stripe_sub_id = session.get('subscription', '')
        expires_at    = timezone.now() + timedelta(days=30)

        sub, _ = Subscription.objects.get_or_create(user=user)
        sub.activate(plan=plan, stripe_sub_id=stripe_sub_id, expires_at=expires_at)

        amount_cents = session.get('amount_total', 0)
        amount_usd   = Decimal(str(amount_cents / 100))

        from apps.accounts.models import Transaction
        Transaction.objects.create(
            user=user,
            amount=-amount_usd,
            transaction_type='subscription',
            description=f"Stripe subscription: {plan} plan (${amount_usd}/oy)",
        )
        logger.info(f"Subscription activated: {plan} for user #{user.pk}")


def _handle_invoice_paid(invoice):
    """
    invoice.paid → oylik obuna yangilanishi
    """
    from apps.accounts.models import Subscription, Transaction

    stripe_customer_id = invoice.get('customer')
    user = _get_user_by_customer(stripe_customer_id)
    if not user:
        return

    stripe_sub_id = invoice.get('subscription', '')
    amount_usd    = Decimal(str(invoice.get('amount_paid', 0) / 100))

    # Subscription muddatini uzaytirish
    try:
        sub = user.subscription
        sub.expires_at = timezone.now() + timedelta(days=30)
        sub.status = 'active'
        sub.save(update_fields=['expires_at', 'status', 'updated_at'])
    except Subscription.DoesNotExist:
        Subscription.objects.create(
            user=user,
            plan=user.subscription_type,
            status='active',
            stripe_subscription_id=stripe_sub_id,
            expires_at=timezone.now() + timedelta(days=30),
        )

    if amount_usd > 0:
        Transaction.objects.create(
            user=user,
            amount=-amount_usd,
            transaction_type='subscription',
            description=f"Oylik obuna yangilandi: {user.subscription_type} (${amount_usd})",
        )
    logger.info(f"invoice.paid: subscription renewed for user #{user.pk}")


def _handle_subscription_changed(subscription_obj, event_type):
    """
    customer.subscription.updated / deleted → status o'zgarishi
    """
    from apps.accounts.models import Subscription

    stripe_customer_id = subscription_obj.get('customer')
    user = _get_user_by_customer(stripe_customer_id)
    if not user:
        return

    status = subscription_obj.get('status', 'inactive')

    try:
        sub = user.subscription
    except Subscription.DoesNotExist:
        return

    if event_type == 'customer.subscription.deleted' or status == 'canceled':
        sub.cancel()
        logger.info(f"Subscription canceled for user #{user.pk}")
    else:
        sub.status = status
        sub.save(update_fields=['status', 'updated_at'])
        logger.info(f"Subscription status={status} for user #{user.pk}")


def _handle_transfer_created(transfer_obj):
    """
    transfer.created → Marketplace seller payout (Stripe Connect)
    """
    amount_usd = Decimal(str(transfer_obj.get('amount', 0) / 100))
    destination = transfer_obj.get('destination', '')
    logger.info(f"Stripe Connect transfer: ${amount_usd} → {destination}")
    # Kelajakda: Marketplace seller tranzaksiyasini yozish


# ── WALLET API ─────────────────────────────────────────────────────────────────

@login_required
def wallet_api(request):
    """AJAX — joriy balans (depazit + foyda)"""
    from apps.accounts.models import UserBalance
    wallet, _ = UserBalance.objects.get_or_create(user=request.user)
    return JsonResponse({
        'deposit':  float(wallet.deposit_balance),
        'earnings': float(wallet.earnings_balance),
        'total':    float(wallet.total_balance),
        'currency': 'USD',
        # backward compat
        'balance':  float(wallet.deposit_balance),
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q, Avg
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.contrib.auth import SESSION_KEY
from .models import User, Skill, PortfolioItem, Transaction
from .forms import RegisterForm, LoginForm, ProfileEditForm, SkillForm, PortfolioItemForm
from apps.projects.models import Project, Task
from apps.assets.models import Asset


def home_view(request):
    """Bosh sahifa"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    stats = {
        'users': User.objects.count(),
        'projects': Project.objects.filter(status='active').count(),
        'assets': Asset.objects.count(),
    }
    latest_projects = Project.objects.filter(
        visibility='public', status='active'
    ).select_related('creator').order_by('-created_at')[:6]

    latest_assets = Asset.objects.filter(
        is_approved=True
    ).select_related('creator').order_by('-created_at')[:6]

    return render(request, 'home.html', {
        'stats': stats,
        'latest_projects': latest_projects,
        'latest_assets': latest_assets,
    })


@never_cache
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            # Session fixation himoyasi
            request.session.cycle_key()
            # Email tasdiqlash xabari yuborish
            try:
                send_verification_email(request, user)
            except Exception:
                pass
            # Xush kelibsiz emaili — Celery orqali asinxron
            try:
                from apps.tasks import send_welcome_email
                send_welcome_email.delay(user.pk)
            except Exception as e:
                print(f"Welcome email queue error: {e}")
            messages.success(request, f"Xush kelibsiz, {user.username}! 🎮 Emailingizni tasdiqlang.")
            return redirect('dashboard')
        else:
            messages.error(request, "Formada xatolik bor. Tekshirib ko'ring.")
    else:
        form = RegisterForm()
    response = render(request, 'auth/register.html', {'form': form})
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            # Session fixation himoyasi — yangi session ID beriladi
            request.session.cycle_key()
            messages.success(request, f"Xush kelibsiz, {user.username}!")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Email yoki parol noto'g'ri.")
    else:
        form = LoginForm()
    response = render(request, 'auth/login.html', {'form': form})
    # Brauzer bu sahifani keshlamasligi uchun
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Logout: POST bilan CSRF himoyasida, GET bilan ham ishlaydi (oddiy link uchun)."""
    logout(request)
    # Session-ni to'liq tozalash
    request.session.flush()
    messages.info(request, "Tizimdan chiqdingiz.")
    response = redirect('home')
    # Barcha session cookie-larni o'chirish
    response.delete_cookie('sessionid')
    return response


@login_required
def dashboard_view(request):
    user = request.user
    
    # Moliyaviy statistika
    total_earned = Transaction.objects.filter(user=user, transaction_type='sale').aggregate(Sum('amount'))['amount__sum'] or 0
    total_spent = Transaction.objects.filter(user=user, transaction_type='purchase').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Loyiha va vazifalar statistikasi
    created_projects_count = Project.objects.filter(creator=user).count()
    joined_projects_count = Project.objects.filter(members__user=user, members__is_approved=True).exclude(creator=user).distinct().count()
    
    total_tasks = Task.objects.filter(assigned_to=user).count()
    completed_tasks = Task.objects.filter(assigned_to=user, status='done').count()
    
    # Ro'yxatlar
    my_projects = Project.objects.filter(creator=user).order_by('-created_at')[:5]
    my_assets = Asset.objects.filter(creator=user).order_by('-created_at')[:5]
    
    # Foydalanuvchi a'zo bo'lgan loyihalar
    involved_projects = Project.objects.filter(
        members__user=user, members__is_approved=True
    ).exclude(creator=user).order_by('-created_at')[:5]

    stats_data = {
        'total_earned': total_earned,
        'total_spent': abs(total_spent),
        'projects_created': created_projects_count,
        'projects_joined': joined_projects_count,
        'tasks_total': total_tasks,
        'tasks_completed': completed_tasks,
        'asset_count': user.asset_count,
        'xp': user.xp,
        'level': user.level,
        'progress': user.level_progress,
    }

    # Haftalik reyting (Leaderboard)
    from datetime import date, timedelta
    from .models import WeeklyLeaderboard
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    leaderboard = WeeklyLeaderboard.objects.filter(week_start=week_start).select_related('user').order_by('rank')[:10]
    if not leaderboard.exists():
        latest_entry = WeeklyLeaderboard.objects.order_by('-week_start').first()
        if latest_entry:
            leaderboard = WeeklyLeaderboard.objects.filter(week_start=latest_entry.week_start).select_related('user').order_by('rank')[:10]

    return render(request, 'dashboard/dashboard.html', {
        'my_projects': my_projects,
        'my_assets': my_assets,
        'involved_projects': involved_projects,
        'user_stats': stats_data,
        'leaderboard': leaderboard,
    })


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    skills = profile_user.skills.all()
    portfolio = profile_user.portfolio_items.all()
    projects = Project.objects.filter(
        creator=profile_user, visibility='public'
    ).order_by('-created_at')[:8]
    assets = Asset.objects.filter(
        creator=profile_user, is_approved=True
    ).order_by('-created_at')[:8]

    # Badges & Reviews
    from .models import UserBadge, FreelancerReview
    badges = UserBadge.objects.filter(user=profile_user).select_related('badge')
    reviews = FreelancerReview.objects.filter(worker=profile_user).select_related('reviewer').order_by('-created_at')[:10]
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0

    from django.utils import timezone
    from datetime import timedelta
    from .models import UserActivity
    from django.db.models.functions import TruncDate

    one_year_ago = timezone.now().date() - timedelta(days=365)
    activities_qs = profile_user.activities.filter(created_at__date__gte=one_year_ago)\
        .annotate(date=TruncDate('created_at'))\
        .values('date')\
        .annotate(count=Count('id'))\
        .values('date', 'count')

    import json
    activity_data_json = json.dumps({str(a['date']): a['count'] for a in activities_qs})

    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user,
        'skills': skills,
        'portfolio': portfolio,
        'projects': projects,
        'assets': assets,
        'badges': badges,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'activity_data': activity_data_json,
        'is_own_profile': request.user == profile_user,
    })


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil yangilandi!")
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def skill_add_view(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            messages.success(request, "Ko'nikma qo'shildi!")
    return redirect('profile_edit')


@login_required
def skill_delete_view(request, pk):
    skill = get_object_or_404(Skill, pk=pk, user=request.user)
    skill.delete()
    messages.success(request, "Ko'nikma o'chirildi.")
    return redirect('profile_edit')


@login_required
def portfolio_add_view(request):
    if request.method == 'POST':
        form = PortfolioItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, "Portfolio elementi qo'shildi!")
    return redirect('profile', username=request.user.username)


# ── PAROLNI TIKLASH ─────────────────────────────────────────────────────────

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.conf import settings as django_settings
from .tokens import email_verification_token, password_reset_token


def password_reset_request_view(request):
    """Parolni tiklash so'rovi — email kiritish"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email)
            uid   = urlsafe_base64_encode(force_bytes(user.pk))
            token = password_reset_token.make_token(user)
            reset_url = request.build_absolute_uri(
                f'/auth/password-reset/{uid}/{token}/'
            )
            send_mail(
                subject='DevForge — Parolni Tiklash',
                message=f'Parolingizni tiklash uchun:\n{reset_url}\n\nHavola 24 soat amal qiladi.',
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            pass  # Xavfsizlik uchun xato ko'rsatmaymiz
        messages.success(request, "Agar bu email ro'yxatdan o'tgan bo'lsa, xabar yuborildi.")
        return redirect('password_reset_done')
    return render(request, 'auth/password_reset.html')


def password_reset_done_view(request):
    return render(request, 'auth/password_reset_done.html')


def password_reset_confirm_view(request, uidb64, token):
    """Yangi parol kiritish"""
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and password_reset_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Parolingiz yangilandi! Endi kirishingiz mumkin.")
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'auth/password_reset_confirm.html', {'form': form, 'valid': True})
    return render(request, 'auth/password_reset_confirm.html', {'valid': False})


# ── EMAIL TASDIQLASH ─────────────────────────────────────────────────────────

def send_verification_email(request, user):
    uid   = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    verify_url = request.build_absolute_uri(
        f'/auth/verify-email/{uid}/{token}/'
    )
    send_mail(
        subject='DevForge — Email Manzilingizni Tasdiqlang',
        message=f'Salom {user.username}!\n\nEmailingizni tasdiqlash uchun:\n{verify_url}\n\nRahmat!',
        from_email=django_settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def verify_email_view(request, uidb64, token):
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and email_verification_token.check_token(user, token):
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        messages.success(request, "Email manzilingiz tasdiqlandi! ✅")
        return redirect('dashboard')

    messages.error(request, "Havola yaroqsiz yoki muddati o'tgan.")
    return redirect('home')


@login_required
def resend_verification_view(request):
    if not request.user.is_verified:
        send_verification_email(request, request.user)
        messages.success(request, "Tasdiqlash xabari yuborildi. Inboxingizni tekshiring.")
    return redirect('dashboard')

@login_required
def subscription_plans(request):
    """Yangi obuna rejalari sahifasiga yo'naltirish"""
    return redirect('payments:plans')

@login_required
def upgrade_subscription(request, plan_type):
    """Obunani yangilash — Stripe Checkout ga yo'naltirish"""
    valid_plans = ['pro', 'studio', 'enterprise', 'gold', 'platinum']
    if plan_type not in valid_plans:
        messages.error(request, "Noto'g'ri obuna turi!")
        return redirect('payments:plans')

    # Mapping eski nomlarni yangilarga
    plan_map = {'gold': 'pro', 'platinum': 'studio'}
    plan_type = plan_map.get(plan_type, plan_type)

    return redirect('payments:subscribe', plan=plan_type)

@login_required
def top_up_balance(request):
    """Wallet'ni to'ldirish — Stripe Deposit sahifasiga yo'naltirish"""
    return redirect('payments:deposit')

@login_required
def wallet_view(request):
    """Ikki hamyon — Depazit va Foyda hamyon ko'rinishi"""
    from .models import Transaction, UserBalance, Subscription
    wallet, _ = UserBalance.objects.get_or_create(user=request.user)
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:60]
    try:
        subscription = request.user.subscription
    except Subscription.DoesNotExist:
        subscription = None

    return render(request, 'accounts/wallet.html', {
        'wallet':       wallet,
        'deposit':      wallet.deposit_balance,
        'earnings':     wallet.earnings_balance,
        'total':        wallet.total_balance,
        'transactions': transactions,
        'subscription': subscription,
        # backward compat
        'balance':      wallet.deposit_balance,
    })


@login_required
def withdraw_view(request):
    """Foyda hamyonidan pul yechish so'rovi (manual review)"""
    from .models import UserBalance
    if request.method != 'POST':
        return redirect('wallet')

    wallet, _ = UserBalance.objects.get_or_create(user=request.user)
    try:
        from decimal import Decimal, InvalidOperation
        amount = Decimal(request.POST.get('amount', '0').strip())
        method = request.POST.get('method', '').strip()
        details = request.POST.get('details', '').strip()
        if amount <= 0:
            raise ValueError
        if amount < Decimal('1'):
            messages.error(request, "Minimal yechish miqdori: $1.00")
            return redirect('wallet')
        wallet.withdraw(
            amount,
            description=f"Pul yechish | {method}: {details[:100]}"
        )
        messages.success(
            request,
            f"✅ ${amount:.2f} yechish so'rovi qabul qilindi. 1-3 ish kuni ichida qayta ishlanadi."
        )
    except (InvalidOperation, ValueError):
        messages.error(request, "Noto'g'ri miqdor kiritildi.")
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"Xato: {e}")

    return redirect('wallet')


@login_required
def transfer_to_deposit_view(request):
    """Foyda hamyonidan Depazit hamyoniga pul o'tkazish"""
    from .models import UserBalance
    if request.method != 'POST':
        return redirect('wallet')

    wallet, _ = UserBalance.objects.get_or_create(user=request.user)
    try:
        from decimal import Decimal, InvalidOperation
        amount = Decimal(request.POST.get('amount', '0').strip())
        if amount <= 0:
            raise ValueError
        wallet.transfer_to_deposit(amount)
        messages.success(request, f"✅ ${amount:.2f} foyda hamyonidan depazit hamyoniga o'tkazildi.")
    except (InvalidOperation, ValueError):
        messages.error(request, "Noto'g'ri miqdor yoki yetarli mablag' yo'q.")
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"Xato: {e}")

    return redirect('wallet')


def set_language_view(request, lang_code):
    """Foydalanuvchi tilini o'zgartirish (uz, ru, en)"""
    from django.utils import translation
    from django.conf import settings

    supported = [code for code, _ in settings.LANGUAGES]
    if lang_code in supported:
        translation.activate(lang_code)
        request.session['_language'] = lang_code
        request.session['django_language'] = lang_code

    # Qaytish manzili
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    if 'set-language' in next_url:
        next_url = '/'

    response = redirect(next_url)
    if lang_code in supported:
        cookie_name = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')
        response.set_cookie(
            cookie_name,
            lang_code,
            max_age=365 * 24 * 60 * 60,
            samesite='Lax'
        )
    return response

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.projects.models import Project
from apps.jobs.models import Job
from apps.assets.models import Asset

@login_required
def smart_dashboard(request):
    user = request.user
    
    if not user.onboarding_completed:
        return redirect('onboarding')
    
    # Common data
    context = {
        'recent_projects': Project.objects.filter(visibility='public').order_by('-created_at')[:5],
        'user_stats': {
            'projects': user.project_count,
            'assets': user.asset_count,
            'xp': user.xp,
            'level': user.level,
            'progress': user.level_progress,
        }
    }
    
    # Role-based recommendations
    if user.role == 'developer':
        context['recommended_jobs'] = Job.objects.filter(status='open', skills_needed__name__in=['Unity', 'Unreal', 'C#']).distinct()[:4]
        context['recommended_assets'] = Asset.objects.filter(category__name__icontains='code')[:4]
    elif user.role == 'artist':
        context['recommended_jobs'] = Job.objects.filter(status='open', skills_needed__name__in=['3D', 'Maya', 'Blender']).distinct()[:4]
        context['recommended_assets'] = Asset.objects.filter(category__name__icontains='3d')[:4]
    else:
        context['recommended_jobs'] = Job.objects.filter(status='open')[:4]
        context['recommended_assets'] = Asset.objects.all()[:4]
        
    return render(request, 'accounts/dashboard.html', context)

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from apps.accounts.models import User, Subscription, UserBalance, SiteConfig
from apps.feed.models import Post
import decimal

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def super_admin_dashboard(request):
    users    = User.objects.all().order_by('-date_joined').select_related('subscription')
    projects = Project.objects.all().order_by('-created_at')
    assets   = Asset.objects.all().order_by('-created_at')
    posts    = Post.objects.all().order_by('-created_at')

    # Har bir user uchun subscription ma'lumotlarini boyitamiz
    users_with_sub = []
    for u in users:
        try:
            sub = u.subscription
        except Subscription.DoesNotExist:
            sub = None
        try:
            wallet = u.wallet
        except UserBalance.DoesNotExist:
            wallet = None
        users_with_sub.append({
            'user': u,
            'sub': sub,
            'wallet': wallet,
            'balance': wallet.deposit_balance if wallet else 0,
        })

    context = {
        'users': users,
        'users_with_sub': users_with_sub,
        'projects': projects,
        'assets': assets,
        'posts': posts,
        'total_users': users.count(),
        'total_projects': projects.count(),
        'total_assets': assets.count(),
        'total_posts': posts.count(),
        'pending_assets': assets.filter(is_approved=False).count(),
        'plan_choices': Subscription.PLAN_CHOICES,
        'all_studios_enabled': SiteConfig.get_bool('all_studios_enabled', default=False),
    }
    return render(request, 'dashboard/super_admin.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@require_POST
def super_admin_toggle_all_studios(request):
    current = SiteConfig.get_bool('all_studios_enabled', default=False)
    new_val = not current
    SiteConfig.set_bool('all_studios_enabled', new_val, description="Show all studios in Studio Suite dropdown")
    if new_val:
        messages.success(request, "Studio Suite: Barcha studiolarni ko'rsatish YOQILDI!")
    else:
        messages.info(request, "Studio Suite: Cheklov yoqildi (faqat 3D Studio ko'rsatiladi).")
    return redirect('super_admin_dashboard')


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def super_admin_delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    return redirect('super_admin_dashboard')

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def super_admin_approve_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    asset.is_approved = not asset.is_approved
    asset.save()
    return redirect('super_admin_dashboard')

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def super_admin_delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('super_admin_dashboard')

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def super_admin_toggle_verify_user(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    target_user.is_verified = not target_user.is_verified
    target_user.save()
    return redirect('super_admin_dashboard')


# ── SUBSCRIPTION BOSHQARUVI (Admin) ──────────────────────────────────────────

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@require_POST
def admin_change_subscription(request, pk):
    """Admin tomonidan foydalanuvchi obunasini o'zgartirish"""
    target_user = get_object_or_404(User, pk=pk)
    plan = request.POST.get('plan', 'free')
    valid_plans = [p[0] for p in Subscription.PLAN_CHOICES]
    if plan not in valid_plans:
        messages.error(request, f"Noto'g'ri plan: {plan}")
        return redirect('super_admin_dashboard')

    sub, _ = Subscription.objects.get_or_create(user=target_user)
    if plan == 'free':
        sub.plan = 'free'
        sub.status = 'inactive'
        sub.save()
        target_user.subscription_type = 'free'
    else:
        from django.utils import timezone
        import datetime
        sub.plan = plan
        sub.status = 'active'
        sub.expires_at = timezone.now() + datetime.timedelta(days=30)
        sub.save()
        target_user.subscription_type = plan
    target_user.save(update_fields=['subscription_type'])
    messages.success(request, f"@{target_user.username} obunasi '{plan}' ga o'zgartirildi.")
    return redirect('super_admin_dashboard')


# ── ADMIN WALLET ADJUST WITH IMMUTABLE AUDIT LOG ─────────────────────────────

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@require_POST
def admin_adjust_wallet(request, pk):
    """
    Admin tomonidan foydalanuvchi hamyonini tuzatish.
    Har bir o'zgarish AdminWalletAuditLog ga yoziladi —
    o'chirib yoki o'zgartirib bo'lmaydi.
    """
    from apps.accounts.models import AdminWalletAuditLog, Transaction
    target_user = get_object_or_404(User, pk=pk)
    wallet, _   = UserBalance.objects.get_or_create(user=target_user)

    wallet_type = request.POST.get('wallet_type', 'deposit')   # 'deposit' | 'earnings'
    action_type = request.POST.get('action_type', 'credit')     # 'credit' | 'debit' | 'refund' | 'correction'
    reason      = request.POST.get('reason', '').strip()

    if not reason:
        messages.error(request, "Sabab (reason) majburiy!")
        return redirect('super_admin_dashboard')

    if wallet_type not in ('deposit', 'earnings'):
        messages.error(request, "Noto'g'ri hamyon turi.")
        return redirect('super_admin_dashboard')

    try:
        amount = decimal.Decimal(request.POST.get('amount', '0'))
        if amount <= 0:
            raise ValueError("Miqdor musbat bo'lishi kerak")
    except (decimal.InvalidOperation, ValueError) as e:
        messages.error(request, f"Noto'g'ri miqdor: {e}")
        return redirect('super_admin_dashboard')

    # Tanlangan hamyon va amalga qarab balance_before/after hisoblash
    if wallet_type == 'deposit':
        balance_before = wallet.deposit_balance
    else:
        balance_before = wallet.earnings_balance

    # Balansni o'zgartirish
    try:
        if action_type in ('credit', 'refund', 'correction') and wallet_type == 'deposit':
            wallet.deposit_balance += amount
            wallet.save(update_fields=['deposit_balance', 'updated_at'])
            target_user.balance = wallet.deposit_balance
            target_user.save(update_fields=['balance'])
        elif action_type in ('credit', 'refund', 'correction') and wallet_type == 'earnings':
            wallet.earnings_balance += amount
            wallet.save(update_fields=['earnings_balance', 'updated_at'])
        elif action_type == 'debit' and wallet_type == 'deposit':
            if wallet.deposit_balance < amount:
                raise ValueError(f"Depazit hamyonda yetarli mablag' yo'q: ${wallet.deposit_balance}")
            wallet.deposit_balance -= amount
            wallet.save(update_fields=['deposit_balance', 'updated_at'])
            target_user.balance = wallet.deposit_balance
            target_user.save(update_fields=['balance'])
        elif action_type == 'debit' and wallet_type == 'earnings':
            if wallet.earnings_balance < amount:
                raise ValueError(f"Foyda hamyonda yetarli mablag' yo'q: ${wallet.earnings_balance}")
            wallet.earnings_balance -= amount
            wallet.save(update_fields=['earnings_balance', 'updated_at'])
        else:
            raise ValueError("Noma'lum amal turi")
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('super_admin_dashboard')

    balance_after = wallet.deposit_balance if wallet_type == 'deposit' else wallet.earnings_balance

    # Admin IP
    ip = (
        request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
        or request.META.get('REMOTE_ADDR', '')
    )

    # Immutable audit log
    AdminWalletAuditLog.objects.create(
        admin=request.user,
        target_user=target_user,
        wallet_type=wallet_type,
        action_type=action_type,
        amount=amount,
        balance_before=balance_before,
        balance_after=balance_after,
        reason=reason,
        ip_address=ip or None,
    )

    # Transaction ham yozamiz (ko'rinish uchun)
    Transaction.objects.create(
        user=target_user,
        amount=amount if action_type != 'debit' else -amount,
        transaction_type='admin_adjustment',
        wallet_type=wallet_type,
        description=f"Admin tuzatish ({action_type}) | {reason[:200]}",
    )

    messages.success(
        request,
        f"✅ @{target_user.username} {wallet_type} hamyoni "
        f"{'+'if action_type!='debit' else '-'}${amount} | Sabab: {reason[:60]}"
    )
    return redirect('super_admin_dashboard')


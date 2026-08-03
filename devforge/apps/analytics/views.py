from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from django.http import JsonResponse
import json
from datetime import timedelta

from apps.accounts.models import User
from apps.projects.models import Project, ProjectMember, Task
from apps.assets.models import Asset
from apps.marketplace.views import Service, Order, Review
from apps.notifications.models import Notification
try:
    from apps.feed.models import Post, Follow
    from apps.jobs.models import Job, Proposal
    HAS_FEED = True
except ImportError:
    HAS_FEED = False


# ── YORDAMCHI ──────────────────────────────────────────────────────────────────

def get_growth(model, days=30):
    """O'sish foizi: oxirgi N kun vs undan oldingi N kun"""
    now = timezone.now()
    current = model.objects.filter(
        created_at__gte=now - timedelta(days=days)
    ).count()
    previous = model.objects.filter(
        created_at__gte=now - timedelta(days=days * 2),
        created_at__lt=now - timedelta(days=days),
    ).count()
    if previous == 0:
        return 100 if current > 0 else 0
    return round((current - previous) / previous * 100, 1)


def daily_counts(model, days=30, date_field='created_at'):
    """Kunlik ro'yxatdan o'tishlar — grafik uchun"""
    now = timezone.now()
    qs = (
        model.objects
        .filter(**{f"{date_field}__gte": now - timedelta(days=days)})
        .annotate(day=TruncDay(date_field))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    # Barcha kunlarni to'ldirish (bo'sh kunlar = 0)
    result = {}
    for i in range(days):
        d = (now - timedelta(days=days - 1 - i)).strftime('%Y-%m-%d')
        result[d] = 0
    for row in qs:
        k = row['day'].strftime('%Y-%m-%d')
        if k in result:
            result[k] = row['count']
    return list(result.keys()), list(result.values())


# ── ASOSIY DASHBOARD ────────────────────────────────────────────────────────────

@staff_member_required
def analytics_dashboard(request):
    now = timezone.now()
    period = int(request.GET.get('period', 30))  # kun

    # ── UMUMIY STATISTIKA ──
    total_users    = User.objects.count()
    total_projects = Project.objects.count()
    total_assets   = Asset.objects.count()
    total_services = Service.objects.count()
    total_orders   = Order.objects.count()
    total_revenue  = Order.objects.filter(status='completed').aggregate(
        s=Sum('amount')
    )['s'] or 0

    # ── O'SISH ──
    user_growth    = get_growth(User, period)
    project_growth = get_growth(Project, period)
    asset_growth   = get_growth(Asset, period)

    # ── OXIRGI N KUN ──
    since = now - timedelta(days=period)
    new_users    = User.objects.filter(created_at__gte=since).count()
    new_projects = Project.objects.filter(created_at__gte=since).count()
    new_assets   = Asset.objects.filter(created_at__gte=since).count()
    new_orders   = Order.objects.filter(created_at__gte=since).count()

    # ── GRAFIK MA'LUMOTLARI ──
    user_days, user_vals       = daily_counts(User, period)
    project_days, project_vals = daily_counts(Project, period)
    asset_days, asset_vals     = daily_counts(Asset, period)
    order_days, order_vals     = daily_counts(Order, period)

    # ── LOYIHA STATISTIKASI ──
    projects_by_genre  = list(
        Project.objects.values('genre')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    projects_by_status = list(
        Project.objects.values('status')
        .annotate(count=Count('id'))
    )

    # ── AKTIV STATISTIKASI ──
    top_assets = Asset.objects.order_by('-downloads')[:10]
    assets_by_format = list(
        Asset.objects.values('format')
        .annotate(count=Count('id'), total_downloads=Sum('downloads'))
        .order_by('-count')
    )

    # ── MARKETPLACE ──
    orders_by_status = list(
        Order.objects.values('status')
        .annotate(count=Count('id'), revenue=Sum('amount'))
    )
    top_services = (
        Service.objects
        .annotate(order_count=Count('orders'), total_rev=Sum('orders__amount'))
        .order_by('-order_count')[:8]
    )
    top_sellers = (
        User.objects
        .annotate(service_count=Count('services'), order_count=Count('services__orders'))
        .filter(service_count__gt=0)
        .order_by('-order_count')[:8]
    )

    # ── FOYDALANUVCHI STATISTIKASI ──
    users_by_role = list(
        User.objects.values('role')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    recent_users = User.objects.order_by('-created_at')[:10]
    top_users_by_projects = (
        User.objects
        .annotate(proj_count=Count('created_projects'))
        .order_by('-proj_count')[:8]
    )

    # ── FAOLIYAT ──
    recent_orders  = Order.objects.select_related('buyer', 'service').order_by('-created_at')[:8]
    recent_notifs  = Notification.objects.select_related('recipient', 'sender').order_by('-created_at')[:10]
    pending_approvals = ProjectMember.objects.filter(is_approved=False).select_related('user', 'project').count()

    # ── VAZIFALAR ──
    tasks_by_status = list(
        Task.objects.values('status')
        .annotate(count=Count('id'))
    )

    # Feed & Jobs stats
    total_posts = Post.objects.count() if HAS_FEED else 0
    total_jobs  = Job.objects.count() if HAS_FEED else 0
    open_jobs   = Job.objects.filter(status='open').count() if HAS_FEED else 0

    return render(request, 'analytics/dashboard.html', {
        # KPI
        'total_users':    total_users,
        'total_projects': total_projects,
        'total_assets':   total_assets,
        'total_services': total_services,
        'total_orders':   total_orders,
        'total_revenue':  total_revenue,
        'user_growth':    user_growth,
        'project_growth': project_growth,
        'asset_growth':   asset_growth,
        'new_users':      new_users,
        'new_projects':   new_projects,
        'new_assets':     new_assets,
        'new_orders':     new_orders,

        # GRAFIKLAR (JSON)
        'user_days_json':    json.dumps(user_days),
        'user_vals_json':    json.dumps(user_vals),
        'project_days_json': json.dumps(project_days),
        'project_vals_json': json.dumps(project_vals),
        'asset_days_json':   json.dumps(asset_days),
        'asset_vals_json':   json.dumps(asset_vals),
        'order_days_json':   json.dumps(order_days),
        'order_vals_json':   json.dumps(order_vals),

        # JADVALLAR
        'projects_by_genre':  projects_by_genre,
        'projects_by_status': projects_by_status,
        'top_assets':         top_assets,
        'assets_by_format':   assets_by_format,
        'orders_by_status':   orders_by_status,
        'top_services':       top_services,
        'top_sellers':        top_sellers,
        'users_by_role':      users_by_role,
        'recent_users':       recent_users,
        'top_users_by_projects': top_users_by_projects,
        'recent_orders':      recent_orders,
        'recent_notifs':      recent_notifs,
        'pending_approvals':  pending_approvals,
        'tasks_by_status':    tasks_by_status,

        'period': period,
        'total_posts': total_posts,
        'total_jobs':  total_jobs,
        'open_jobs':   open_jobs,
    })


# ── AJAX API ───────────────────────────────────────────────────────────────────

@staff_member_required
def analytics_api(request):
    """AJAX endpoint — period o'zgarganda grafik ma'lumotlarini qaytaradi"""
    period = int(request.GET.get('period', 30))
    u_days, u_vals = daily_counts(User, period)
    p_days, p_vals = daily_counts(Project, period)
    a_days, a_vals = daily_counts(Asset, period)
    o_days, o_vals = daily_counts(Order, period)
    return JsonResponse({
        'users':    {'days': u_days, 'vals': u_vals},
        'projects': {'days': p_days, 'vals': p_vals},
        'assets':   {'days': a_days, 'vals': a_vals},
        'orders':   {'days': o_days, 'vals': o_vals},
    })


# ── FOYDALANUVCHILARNI BOSHQARISH ─────────────────────────────────────────────

@staff_member_required
def user_management(request):
    query  = request.GET.get('q', '')
    role   = request.GET.get('role', '')
    status = request.GET.get('status', '')

    users = User.objects.annotate(
        proj_count=Count('created_projects', distinct=True),
        total_assets=Count('assets', distinct=True),
        order_count=Count('orders_placed', distinct=True),
    ).order_by('-created_at')

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query)
        )
    if role:
        users = users.filter(role=role)
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    elif status == 'staff':
        users = users.filter(is_staff=True)

    return render(request, 'analytics/users.html', {
        'users':        users,
        'query':        query,
        'role':         role,
        'status':       status,
        'role_choices': User.ROLE_CHOICES,
        'total':        users.count(),
    })


@staff_member_required
def toggle_user_active(request, pk):
    """Foydalanuvchini faollashtirish / bloklash"""
    user = User.objects.get(pk=pk)
    if user != request.user:
        user.is_active = not user.is_active
        user.save()
    return redirect('user_management')


@staff_member_required
def toggle_user_verified(request, pk):
    """Foydalanuvchini tasdiqlash / bekor qilish"""
    user = User.objects.get(pk=pk)
    user.is_verified = not user.is_verified
    user.save()
    return redirect('user_management')


# ── LOYIHALARNI BOSHQARISH ────────────────────────────────────────────────────

@staff_member_required
def project_management(request):
    projects = Project.objects.select_related('creator').annotate(
        total_members=Count('members', distinct=True),
        task_count=Count('tasks', distinct=True),
    ).order_by('-created_at')

    query  = request.GET.get('q', '')
    status = request.GET.get('status', '')
    if query:
        projects = projects.filter(Q(title__icontains=query) | Q(creator__username__icontains=query))
    if status:
        projects = projects.filter(status=status)

    return render(request, 'analytics/projects.html', {
        'projects': projects,
        'query': query,
        'status': status,
        'status_choices': Project.STATUS_CHOICES,
    })


@staff_member_required
def update_user_subscription(request, pk):
    """Admin foydalanuvchi obunasini o'zgartiradi"""
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        new_plan = request.POST.get('subscription_type')
        if new_plan in dict(User.SUBSCRIPTION_CHOICES):
            user.subscription_type = new_plan
            user.save()
            messages.success(request, f"{user.username} obunasi {new_plan}ga o'zgartirildi.")
    return redirect('user_management')

@staff_member_required
def update_user_balance(request, pk):
    """Admin foydalanuvchi balansini tahrirlash — audit log orqali"""
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    user = get_object_or_404(User, pk=pk)
    # To'g'ridan-to'g'ri balans tahrirlash taqiqlangan.
    # Super Admin panelidagi 'adjust()' tugmasini ishlating.
    messages.warning(
        request,
        f"⚠️ Balansni to'g'ridan-to'g'ri tahrirlash taqiqlangan. "
        f"Super Admin panelida '@{user.username}' uchun 'adjust()' tugmasidan foydalaning "
        f"(har o'zgarish audit log'ga yoziladi)."
    )
    return redirect('user_management')

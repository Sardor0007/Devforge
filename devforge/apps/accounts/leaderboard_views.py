from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum, Count
from datetime import timedelta, date

from apps.accounts.models import User, WeeklyLeaderboard


# ── LEADERBOARD ───────────────────────────────────────────────────────────────

def leaderboard_view(request):
    """Reyting jadvali sahifasi"""
    tab = request.GET.get('tab', 'xp')  # xp | sales | posts

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    if tab == 'xp':
        # Umumiy XP reytingi
        users = User.objects.filter(is_active=True).order_by('-xp')[:100]
        title = "🏆 XP Reytingi"
        subtitle = "Eng ko'p tajriba to'plagan foydalanuvchilar"

    elif tab == 'sales':
        # Eng ko'p sotgan
        from apps.accounts.models import Transaction
        from django.db.models import Q
        users = User.objects.filter(is_active=True).annotate(
            total_sales=Sum(
                'transactions__amount',
                filter=Q(transactions__transaction_type='sale')
            )
        ).filter(total_sales__gt=0).order_by('-total_sales')[:100]
        title = "💰 Savdo Reytingi"
        subtitle = "Eng ko'p daromad qilgan freelancerlar"

    elif tab == 'posts':
        # Eng faol postlovchilar
        users = User.objects.filter(is_active=True).annotate(
            post_count=Count('posts')
        ).filter(post_count__gt=0).order_by('-post_count')[:100]
        title = "📝 Post Reytingi"
        subtitle = "Eng faol hamjamiyat a'zolari"

    elif tab == 'weekly':
        # Haftalik reyting (WeeklyLeaderboard dan)
        entries = WeeklyLeaderboard.objects.filter(
            week_start=week_start
        ).select_related('user').order_by('rank')[:100]
        return render(request, 'leaderboard/index.html', {
            'entries': entries,
            'tab': tab,
            'title': "📅 Haftalik Reyting",
            'subtitle': f"Bu hafta ({week_start.strftime('%d.%m.%Y')}) eng faol foydalanuvchilar",
            'week_start': week_start,
        })

    else:
        users = User.objects.filter(is_active=True).order_by('-xp')[:100]
        title = "🏆 XP Reytingi"
        subtitle = "Eng ko'p tajriba to'plagan foydalanuvchilar"

    # Current user's rank
    current_rank = None
    if request.user.is_authenticated:
        user_xp = request.user.xp
        current_rank = User.objects.filter(is_active=True, xp__gt=user_xp).count() + 1

    return render(request, 'leaderboard/index.html', {
        'users': users,
        'tab': tab,
        'title': title,
        'subtitle': subtitle,
        'current_rank': current_rank,
        'week_start': week_start,
    })


@login_required
def my_rank_api(request):
    """Foydalanuvchi o'z reytingini oladi (AJAX)"""
    user = request.user
    xp_rank   = User.objects.filter(is_active=True, xp__gt=user.xp).count() + 1
    post_count = user.posts.count()
    from apps.accounts.models import Transaction
    from django.db.models import Q
    total_sales = Transaction.objects.filter(
        user=user, transaction_type='sale'
    ).aggregate(s=Sum('amount'))['s'] or 0

    return JsonResponse({
        'xp_rank': xp_rank,
        'xp': user.xp,
        'level': user.level,
        'post_count': post_count,
        'total_sales': float(total_sales),
    })

from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from apps.accounts.models import User
from apps.projects.models import Project
from apps.assets.models import Asset
from apps.marketplace.models import Service
from apps.feed.models import Post
from apps.jobs.models import Job

try:
    from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

def global_search_view(request):
    query = request.GET.get('q', '').strip()
    tab   = request.GET.get('tab', 'all')
    page  = request.GET.get('page', 1)

    results = {'users':[], 'projects':[], 'assets':[], 'services':[], 'posts':[], 'jobs':[]}
    counts  = {'users':0,  'projects':0,  'assets':0,  'services':0, 'posts':0, 'jobs':0}
    total   = 0

    if query:
        if HAS_POSTGRES:
            # PostgreSQL Full-Text Search
            projects = Project.objects.annotate(
                rank=SearchRank(SearchVector('title', weight='A') + SearchVector('description', weight='B'), SearchQuery(query))
            ).filter(rank__gte=0.1, visibility='public').order_by('-rank')
            
            users = User.objects.annotate(
                similarity=TrigramSimilarity('username', query)
            ).filter(similarity__gt=0.1).order_by('-similarity')
            
            assets = Asset.objects.annotate(
                rank=SearchRank(SearchVector('title', weight='A') + SearchVector('description', weight='B'), SearchQuery(query))
            ).filter(rank__gte=0.1, is_approved=True).order_by('-rank')
            
            services = Service.objects.annotate(
                rank=SearchRank(SearchVector('title', weight='A') + SearchVector('description', weight='B'), SearchQuery(query))
            ).filter(rank__gte=0.1, is_active=True).order_by('-rank')
            
            posts = Post.objects.filter(is_public=True, content__icontains=query) # Post content can be large, use simple icontains for now
            jobs = Job.objects.filter(status='open', title__icontains=query)
        else:
            # Fallback for SQLite
            users = User.objects.filter(
                Q(username__icontains=query)|Q(first_name__icontains=query)|
                Q(last_name__icontains=query)|Q(bio__icontains=query)
            )
            projects = Project.objects.filter(visibility='public').filter(
                Q(title__icontains=query)|Q(description__icontains=query)|Q(tech_stack__icontains=query)
            ).select_related('creator')
            assets = Asset.objects.filter(is_approved=True).filter(
                Q(title__icontains=query)|Q(description__icontains=query)
            ).select_related('creator')
            services = Service.objects.filter(is_active=True).filter(
                Q(title__icontains=query)|Q(description__icontains=query)
            ).select_related('seller')
            posts = Post.objects.filter(is_public=True, content__icontains=query).select_related('author')
            jobs = Job.objects.filter(status='open', title__icontains=query).select_related('client')

        counts = {
            'users':    users.count(),
            'projects': projects.count(),
            'assets':   assets.count(),
            'services': services.count(),
            'posts':    posts.count(),
            'jobs':     jobs.count(),
        }
        total = sum(counts.values())

        per_page = 12
        qs_map = {
            'users': users, 'projects': projects, 'assets': assets,
            'services': services, 'posts': posts, 'jobs': jobs
        }

        if tab in qs_map and tab != 'all':
            paginator = Paginator(qs_map[tab], per_page)
            results[tab] = paginator.get_page(page)
        else:
            for key, qs in qs_map.items():
                results[key] = qs[:6]

    return render(request, 'search/results.html', {
        'query':   query,
        'tab':     tab,
        'results': results,
        'counts':  counts,
        'total':   total,
    })

def search_suggestions_api(request):
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return JsonResponse({'results': []})

    users = User.objects.filter(username__icontains=q)[:3]
    projects = Project.objects.filter(title__icontains=q, visibility='public')[:3]
    assets = Asset.objects.filter(title__icontains=q, is_approved=True)[:3]

    results = []
    for u in users:
        results.append({'title': u.username, 'type': 'User', 'url': f"/profile/{u.username}/"})
    for p in projects:
        results.append({'title': p.title, 'type': 'Project', 'url': f"/projects/{p.pk}/"})
    for a in assets:
        results.append({'title': a.title, 'type': 'Asset', 'url': f"/assets/{a.pk}/"})

    return JsonResponse({'results': results})

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q

from .models import GameProject, GameScene, GameBuild, GameLike, GameComment


# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    my_games        = GameProject.objects.filter(owner=request.user).select_related('owner')
    public_qs       = GameProject.objects.filter(is_public=True).exclude(owner=request.user).select_related('owner')

    genre_filter = request.GET.get('genre', '')
    if genre_filter:
        public_qs = public_qs.filter(genre=genre_filter)

    featured     = public_qs.filter(is_featured=True)[:6]
    public_games = public_qs[:20]

    genre_choices = GameProject.GENRE_CHOICES

    ctx = {
        'my_games':     my_games,
        'public_games': public_games,
        'featured':     featured,
        'genre_choices': genre_choices,
        'active_genre': genre_filter,
        'page_title':   'Game Engine',
    }
    return render(request, 'game_engine/dashboard.html', ctx)


# ── Editor ────────────────────────────────────────────────────────────────────

@login_required
def editor(request, pk=None):
    if pk:
        proj = get_object_or_404(GameProject, pk=pk, owner=request.user)
        main_scene = proj.scenes.filter(is_main=True).first() or proj.scenes.first()
    else:
        # Create a fresh project
        proj = GameProject.objects.create(
            owner=request.user, title='Untitled Game', genre='other'
        )
        main_scene = GameScene.objects.create(
            project=proj, name='Main Scene', order=0, is_main=True,
            scene_data={'entities': [], 'settings': {
                'gravity': 0.5, 'width': 800, 'height': 600,
                'backgroundColor': '#1a1a2e', 'fps': 60
            }}
        )

    scenes  = list(proj.scenes.values('id', 'name', 'order', 'is_main'))
    assets  = list(proj.assets.values('id', 'name', 'asset_type', 'file', 'width', 'height'))
    scripts = list(proj.scripts.values('id', 'name', 'script_type'))

    # Build asset URLs
    from django.conf import settings as django_settings
    for a in assets:
        if a['file']:
            a['url'] = request.build_absolute_uri(django_settings.MEDIA_URL + a['file'])
        else:
            a['url'] = ''
        del a['file']

    ctx = {
        'project':       proj,
        'main_scene':    main_scene,
        'scenes_json':   json.dumps(scenes),
        'assets_json':   json.dumps(assets),
        'scripts_json':  json.dumps(scripts),
        'scene_data_json': json.dumps(main_scene.scene_data if main_scene else {}),
        'page_title':    f'Editor — {proj.title}',
    }
    return render(request, 'game_engine/editor.html', ctx)


# ── Game Detail ───────────────────────────────────────────────────────────────

def game_detail(request, pk):
    proj     = get_object_or_404(GameProject, pk=pk)
    if not proj.is_public and (not request.user.is_authenticated or proj.owner != request.user):
        return redirect('game_engine:dashboard')

    comments = proj.comments.select_related('author')[:50]
    liked    = False
    if request.user.is_authenticated:
        liked = GameLike.objects.filter(project=proj, user=request.user).exists()

    # Related games
    related = GameProject.objects.filter(
        is_public=True, genre=proj.genre
    ).exclude(pk=pk)[:6]

    ctx = {
        'project':  proj,
        'comments': comments,
        'liked':    liked,
        'related':  related,
        'page_title': proj.title,
    }
    return render(request, 'game_engine/detail.html', ctx)


# ── Play ──────────────────────────────────────────────────────────────────────

def play(request, pk):
    proj = get_object_or_404(GameProject, pk=pk)
    if not proj.is_public and (not request.user.is_authenticated or proj.owner != request.user):
        return redirect('game_engine:dashboard')

    build = proj.builds.filter(is_active=True).first()
    main_scene = proj.scenes.filter(is_main=True).first() or proj.scenes.first()

    # Build runtime asset list
    from django.conf import settings as django_settings
    assets = []
    for a in proj.assets.all():
        assets.append({
            'id': a.id, 'name': a.name, 'type': a.asset_type,
            'url': request.build_absolute_uri(a.file.url) if a.file else '',
        })

    scripts = list(proj.scripts.values('id', 'name', 'code'))

    ctx = {
        'project':         proj,
        'build':           build,
        'scene_data_json': json.dumps(main_scene.scene_data if main_scene else {}),
        'assets_json':     json.dumps(assets),
        'scripts_json':    json.dumps(scripts),
        'all_scenes_json': json.dumps([
            {'id': s.id, 'name': s.name, 'is_main': s.is_main, 'data': s.scene_data}
            for s in proj.scenes.all()
        ]),
        'page_title':      f'Play — {proj.title}',
    }
    return render(request, 'game_engine/play.html', ctx)

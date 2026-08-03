import json
import os
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import (
    GameProject, GameScene, GameAsset,
    GameScript, GameBuild, GameLike, GameComment, GamePlaySession
)
from .serializers import (
    GameProjectDetailSerializer, GameAssetSerializer,
    GameSceneSerializer, GameScriptSerializer, GameCommentSerializer
)


# ── Project CRUD ─────────────────────────────────────────────────────────────

@login_required
@require_http_methods(["POST"])
def api_create_project(request):
    data  = json.loads(request.body)
    title = data.get('title', 'Untitled Game').strip() or 'Untitled Game'
    genre = data.get('genre', 'other')
    proj  = GameProject.objects.create(
        owner=request.user, title=title, genre=genre,
        description=data.get('description', '')
    )
    # Create default main scene
    GameScene.objects.create(project=proj, name='Main Scene', order=0, is_main=True,
                             scene_data={'entities': [], 'settings': {
                                 'gravity': 0.5, 'width': 800, 'height': 600,
                                 'backgroundColor': '#1a1a2e', 'fps': 60
                             }})
    return JsonResponse({'id': proj.id, 'title': proj.title}, status=201)


@login_required
@require_http_methods(["GET"])
def api_project_detail(request, pk):
    proj = get_object_or_404(GameProject, pk=pk)
    if not proj.is_public and proj.owner != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    ser = GameProjectDetailSerializer(proj, context={'request': request})
    return JsonResponse(ser.data)


@login_required
@require_http_methods(["PATCH"])
def api_update_project(request, pk):
    proj = get_object_or_404(GameProject, pk=pk, owner=request.user)
    data = json.loads(request.body)
    for field in ('title', 'description', 'genre', 'is_public'):
        if field in data:
            setattr(proj, field, data[field])
    proj.save()
    return JsonResponse({'ok': True})


@login_required
@require_http_methods(["DELETE"])
def api_delete_project(request, pk):
    proj = get_object_or_404(GameProject, pk=pk, owner=request.user)
    proj.delete()
    return JsonResponse({'ok': True})


# ── Scene CRUD ────────────────────────────────────────────────────────────────

@login_required
@require_http_methods(["POST"])
def api_save_scene(request, pk):
    """Save (upsert) scene data for a project."""
    proj = get_object_or_404(GameProject, pk=pk, owner=request.user)
    data     = json.loads(request.body)
    scene_id = data.get('scene_id')
    if scene_id:
        scene = get_object_or_404(GameScene, pk=scene_id, project=proj)
    else:
        scene = proj.scenes.filter(is_main=True).first()
        if not scene:
            scene = GameScene.objects.create(project=proj, name='Main Scene', is_main=True)
    scene.scene_data = data.get('scene_data', scene.scene_data)
    scene.name       = data.get('name', scene.name)
    scene.save()
    return JsonResponse({'ok': True, 'scene_id': scene.id, 'updated_at': scene.updated_at.isoformat()})


@login_required
@require_http_methods(["POST"])
def api_create_scene(request, pk):
    proj  = get_object_or_404(GameProject, pk=pk, owner=request.user)
    data  = json.loads(request.body)
    count = proj.scenes.count()
    scene = GameScene.objects.create(
        project=proj, name=data.get('name', f'Scene {count + 1}'),
        order=count,
        scene_data={'entities': [], 'settings': {
            'gravity': 0.5, 'width': 800, 'height': 600,
            'backgroundColor': '#1a1a2e', 'fps': 60
        }}
    )
    return JsonResponse({'id': scene.id, 'name': scene.name}, status=201)


@login_required
@require_http_methods(["DELETE"])
def api_delete_scene(request, pk, scene_pk):
    proj  = get_object_or_404(GameProject, pk=pk, owner=request.user)
    scene = get_object_or_404(GameScene, pk=scene_pk, project=proj)
    if scene.is_main and proj.scenes.count() == 1:
        return JsonResponse({'error': 'Cannot delete the only scene'}, status=400)
    scene.delete()
    return JsonResponse({'ok': True})


# ── Asset Upload ──────────────────────────────────────────────────────────────

@login_required
@require_http_methods(["POST"])
def api_upload_asset(request, pk):
    proj = get_object_or_404(GameProject, pk=pk, owner=request.user)
    f    = request.FILES.get('file')
    if not f:
        return JsonResponse({'error': 'No file provided'}, status=400)

    ext  = os.path.splitext(f.name)[1].lower()
    atype_map = {
        '.png': 'sprite', '.jpg': 'sprite', '.jpeg': 'sprite', '.gif': 'sprite', '.webp': 'sprite', '.svg': 'sprite',
        '.mp3': 'audio',  '.wav': 'audio',  '.ogg': 'audio',
        '.json': 'tilemap',
        '.ttf': 'font', '.woff': 'font',
        '.js': 'script',
    }
    atype = atype_map.get(ext, 'other')

    asset = GameAsset.objects.create(
        project=proj, name=request.POST.get('name', f.name),
        asset_type=atype, file=f, file_size=f.size
    )
    ser = GameAssetSerializer(asset, context={'request': request})
    return JsonResponse(ser.data, status=201)


@login_required
@require_http_methods(["DELETE"])
def api_delete_asset(request, pk, asset_pk):
    proj  = get_object_or_404(GameProject, pk=pk, owner=request.user)
    asset = get_object_or_404(GameAsset, pk=asset_pk, project=proj)
    if asset.file:
        try:
            os.remove(asset.file.path)
        except OSError:
            pass
    asset.delete()
    return JsonResponse({'ok': True})


# ── Script CRUD ───────────────────────────────────────────────────────────────

@login_required
@require_http_methods(["POST"])
def api_save_script(request, pk):
    proj = get_object_or_404(GameProject, pk=pk, owner=request.user)
    data = json.loads(request.body)
    sid  = data.get('id')
    if sid:
        script = get_object_or_404(GameScript, pk=sid, project=proj)
    else:
        script = GameScript(project=proj, name=data.get('name', 'New Script'))
    script.code      = data.get('code', script.code)
    script.node_data = data.get('node_data', script.node_data)
    script.name      = data.get('name', script.name)
    script.save()
    return JsonResponse({'ok': True, 'id': script.id})


# ── Build & Publish ───────────────────────────────────────────────────────────

@login_required
@require_http_methods(["POST"])
def api_build_project(request, pk):
    proj = get_object_or_404(GameProject, pk=pk, owner=request.user)
    data = json.loads(request.body)

    # Deactivate old builds
    proj.builds.update(is_active=False)

    build_data = {
        'title':   proj.title,
        'genre':   proj.genre,
        'scenes':  [{'id': s.id, 'name': s.name, 'is_main': s.is_main, 'data': s.scene_data}
                    for s in proj.scenes.all()],
        'assets':  [{'id': a.id, 'name': a.name, 'type': a.asset_type, 'url': a.file.url if a.file else ''}
                    for a in proj.assets.all()],
        'scripts': [{'id': sc.id, 'name': sc.name, 'code': sc.code}
                    for sc in proj.scripts.all()],
    }
    build = GameBuild.objects.create(project=proj, version=data.get('version', '1.0.0'),
                                     build_data=build_data, is_active=True)
    proj.is_public = data.get('publish', proj.is_public)
    proj.save()
    return JsonResponse({'ok': True, 'build_id': build.id, 'version': build.version})


# ── Play / Social ─────────────────────────────────────────────────────────────

@require_http_methods(["POST"])
def api_record_play(request, pk):
    proj = get_object_or_404(GameProject, pk=pk)
    proj.play_count += 1
    proj.save(update_fields=['play_count'])
    player = request.user if request.user.is_authenticated else None
    GamePlaySession.objects.create(project=proj, player=player)
    return JsonResponse({'play_count': proj.play_count})


@login_required
@require_http_methods(["POST"])
def api_toggle_like(request, pk):
    proj  = get_object_or_404(GameProject, pk=pk)
    liked = GameLike.objects.filter(project=proj, user=request.user)
    if liked.exists():
        liked.delete()
        proj.like_count = max(0, proj.like_count - 1)
        proj.save(update_fields=['like_count'])
        return JsonResponse({'liked': False, 'like_count': proj.like_count})
    GameLike.objects.create(project=proj, user=request.user)
    proj.like_count += 1
    proj.save(update_fields=['like_count'])
    return JsonResponse({'liked': True, 'like_count': proj.like_count})


@login_required
@require_http_methods(["POST"])
def api_add_comment(request, pk):
    proj = get_object_or_404(GameProject, pk=pk)
    data = json.loads(request.body)
    body = data.get('body', '').strip()
    if not body:
        return JsonResponse({'error': 'Comment body required'}, status=400)
    comment = GameComment.objects.create(project=proj, author=request.user, body=body)
    ser = GameCommentSerializer(comment, context={'request': request})
    return JsonResponse(ser.data, status=201)


@require_http_methods(["GET"])
def api_comments(request, pk):
    proj     = get_object_or_404(GameProject, pk=pk)
    comments = proj.comments.select_related('author').all()
    ser = GameCommentSerializer(comments, many=True, context={'request': request})
    return JsonResponse({'comments': ser.data})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import Scene3D


@login_required
def dashboard(request):
    scenes = Scene3D.objects.filter(creator=request.user)
    return render(request, 'studio_3d/dashboard.html', {'scenes': scenes})


@login_required
def editor_view(request, scene_id):
    scene = get_object_or_404(Scene3D, id=scene_id, creator=request.user)
    return render(request, 'studio_3d/editor.html', {'scene': scene})


@login_required
def create_scene(request):
    if request.method == 'POST':
        title    = request.POST.get('title', '').strip() or 'Untitled Scene'
        template = request.POST.get('template', 'empty')
        scene = Scene3D.objects.create(
            creator=request.user,
            title=title,
            template=template,
            scene_data={},
        )
        return redirect('studio_3d:editor', scene_id=scene.id)
    return redirect('studio_3d:dashboard')


@login_required
@require_POST
def save_scene(request, scene_id):
    scene = get_object_or_404(Scene3D, id=scene_id, creator=request.user)
    try:
        payload = json.loads(request.body)
        scene_data = payload.get('scene_data', {})
        scene.scene_data = scene_data
        title = payload.get('title', '').strip()
        if title:
            scene.title = title
        scene.save()
        return JsonResponse({'status': 'saved', 'updated_at': scene.updated_at.isoformat()})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def delete_scene(request, scene_id):
    scene = get_object_or_404(Scene3D, id=scene_id, creator=request.user)
    scene.delete()
    return redirect('studio_3d:dashboard')

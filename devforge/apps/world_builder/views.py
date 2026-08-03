from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import logging

from .models import WorldMap

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    maps = WorldMap.objects.filter(owner=request.user).order_by('-updated_at')
    return render(request, 'world_builder/dashboard.html', {'maps': maps})


@login_required
def editor_view(request, map_id):
    world_map = get_object_or_404(WorldMap, id=map_id, owner=request.user)
    import json as _json
    return render(request, 'world_builder/editor.html', {
        'map': world_map,
        'map_data_json': _json.dumps(world_map.data or {})
    })



@login_required
def create_map(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip() or 'Untitled Map'
        map_type = request.POST.get('map_type', 'level')
        default_data = {
            'version': 2,
            'gridSize': 32,
            'activeLayer': 'ly_walls',
            'layers': [
                {'id': 'ly_ground',   'name': 'Ground',   'visible': True, 'locked': False, 'color': '#22c55e'},
                {'id': 'ly_walls',    'name': 'Walls',    'visible': True, 'locked': False, 'color': '#00d4ff'},
                {'id': 'ly_objects',  'name': 'Objects',  'visible': True, 'locked': False, 'color': '#f59e0b'},
                {'id': 'ly_notes',    'name': 'Notes',    'visible': True, 'locked': False, 'color': '#a78bfa'},
            ],
            'objects': [],
            'groups': [],
        }
        world_map = WorldMap.objects.create(
            title=title,
            owner=request.user,
            map_type=map_type,
            data=default_data,
        )
        return redirect('world_builder:editor', map_id=world_map.id)
    return redirect('world_builder:dashboard')


@login_required
@require_POST
def save_map(request, map_id):
    world_map = get_object_or_404(WorldMap, id=map_id, owner=request.user)
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("save_map: invalid JSON — %s", e)
        return JsonResponse({'status': 'error', 'message': 'Noto\'g\'ri JSON format'}, status=400)

    data = payload.get('data')
    if data is None:
        return JsonResponse({'status': 'error', 'message': '\'data\' maydoni yo\'q'}, status=400)

    # Validate version
    if not isinstance(data, dict):
        return JsonResponse({'status': 'error', 'message': 'Data dict bo\'lishi shart'}, status=400)

    # Optionally update the map title if sent
    new_title = payload.get('title', '').strip()
    if new_title:
        world_map.title = new_title

    world_map.data = data
    try:
        world_map.save()
    except Exception as e:
        logger.error("save_map: DB save error — %s", e)
        return JsonResponse({'status': 'error', 'message': 'Bazaga saqlashda xatolik'}, status=500)

    return JsonResponse({
        'status': 'success',
        'message': 'Saqlandi',
        'updated_at': world_map.updated_at.isoformat(),
    })


@login_required
def delete_map(request, map_id):
    world_map = get_object_or_404(WorldMap, id=map_id, owner=request.user)
    world_map.delete()
    return redirect('world_builder:dashboard')


@login_required
def rename_map(request, map_id):
    """AJAX endpoint to rename a map title."""
    world_map = get_object_or_404(WorldMap, id=map_id, owner=request.user)
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            title = payload.get('title', '').strip()
            if not title:
                return JsonResponse({'status': 'error', 'message': 'Nom bo\'sh bo\'lmaydi'}, status=400)
            world_map.title = title
            world_map.save(update_fields=['title', 'updated_at'])
            return JsonResponse({'status': 'success', 'title': world_map.title})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'POST kerak'}, status=405)

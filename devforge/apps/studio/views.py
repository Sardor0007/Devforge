import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction
from django.utils import timezone
from .models import StudioProject, StudioObject


# ──────────────────────────────────────────────────────────────────────────────
# DASHBOARD  /studio/
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def project_list(request):
    """Studio dashboard – list all projects owned by the user."""
    projects = StudioProject.objects.filter(owner=request.user).order_by('-updated_at')
    total_objects = StudioObject.objects.filter(project__owner=request.user).count()

    # Quick stats for the dashboard header
    stats = {
        'project_count': projects.count(),
        'object_count':  total_objects,
    }
    return render(request, 'studio/dashboard.html', {
        'projects': projects,
        'stats':    stats,
        'total_objects': total_objects,
    })


# ──────────────────────────────────────────────────────────────────────────────
# CREATE  POST /studio/create/
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def create_project(request):
    """Create a new studio project.
    Accepts both form POST and JSON POST (for async creation).
    """
    if request.method == 'POST':
        # Support both JSON body and form data
        if request.content_type and 'application/json' in request.content_type:
            try:
                body = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
        else:
            body = request.POST

        title       = (body.get('title') or 'Yangi 3D Loyiha').strip() or 'Yangi 3D Loyiha'
        description = body.get('description', '')

        default_settings = {
            "bg_color":          "#1D1D1D",
            "ambient_intensity": 0.4,
            "ambient_color":     "#ffffff",
            "grid_visible":      True,
            "fog_enabled":       False,
            "fog_color":         "#1D1D1D",
            "fog_near":          10,
            "fog_far":           100,
            "shadow_enabled":    True,
            "tone_mapping":      "aces",
        }

        project = StudioProject.objects.create(
            title=title,
            description=description,
            owner=request.user,
            settings_data=default_settings,
        )

        # JSON response (for AJAX callers)
        if request.content_type and 'application/json' in request.content_type:
            return JsonResponse({
                'id':    project.id,
                'title': project.title,
                'url':   f'/studio/editor/{project.id}/',
            })

        return redirect('studio:editor', project_id=project.id)

    return redirect('studio:index')


# ──────────────────────────────────────────────────────────────────────────────
# DELETE  POST /studio/delete/<id>/
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def delete_project(request, project_id):
    project = get_object_or_404(StudioProject, id=project_id, owner=request.user)
    if request.method == 'POST':
        # Also remove any uploaded asset files to free disk space
        for obj in project.scene_objects.all():
            if obj.asset_file:
                try:
                    obj.asset_file.delete(save=False)
                except Exception:
                    pass
        project.delete()

        if request.content_type and 'application/json' in request.content_type:
            return JsonResponse({'status': 'deleted'})

    return redirect('studio:index')


# ──────────────────────────────────────────────────────────────────────────────
# EDITOR  GET /studio/editor/<id>/
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@ensure_csrf_cookie
def editor_view(request, project_id):
    """Render the full 3D Studio editor page."""
    project = get_object_or_404(StudioProject, id=project_id, owner=request.user)
    objects = project.scene_objects.all()

    serialized_objects = []
    for obj in objects:
        serialized_objects.append({
            "id":              obj.id,
            "name":            obj.name,
            "object_type":     obj.object_type,
            "transform_data":  obj.transform_data or {},
            "properties_data": obj.properties_data or {},
            "asset_url":       obj.asset_file.url if obj.asset_file else None,
        })

    context = {
        'project':       project,
        'initial_data':  json.dumps(serialized_objects),
        'settings_data': json.dumps(project.settings_data or {}),
    }
    return render(request, 'studio/index.html', context)


# ──────────────────────────────────────────────────────────────────────────────
# SAVE  POST /studio/save/<id>/
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@require_POST
def save_project(request, project_id):
    """Full scene save – replaces all scene objects atomically."""
    try:
        project = get_object_or_404(StudioProject, id=project_id, owner=request.user)
        data    = json.loads(request.body)

        with transaction.atomic():
            # Update scene-level settings
            if 'settings' in data and isinstance(data['settings'], dict):
                # Merge – don't wipe keys the frontend didn't touch
                current = project.settings_data or {}
                current.update(data['settings'])
                project.settings_data = current

            # Update title
            new_title = (data.get('title') or '').strip()
            if new_title:
                project.title = new_title

            project.save()

            # Sync scene objects (full replace)
            if 'objects' in data and isinstance(data['objects'], list):
                project.scene_objects.all().delete()
                bulk = []
                for obj_data in data['objects']:
                    td = obj_data.get('transform_data') or {}
                    pd = obj_data.get('properties_data') or {}

                    # Normalise object_type from frontend
                    raw_type = obj_data.get('object_type', 'primitive')
                    if raw_type in ('box','sphere','cylinder','cone','torus','plane',
                                    'capsule','icosphere','torusknot'):
                        obj_type = 'primitive'
                    elif raw_type.startswith('light_'):
                        obj_type = 'light'
                    else:
                        obj_type = raw_type if raw_type in ('mesh','primitive','light') else 'primitive'

                    # Store the original geometry type inside properties_data
                    pd.setdefault('geometry', raw_type)

                    bulk.append(StudioObject(
                        project=project,
                        name=obj_data.get('name', 'Object'),
                        object_type=obj_type,
                        transform_data=td,
                        properties_data=pd,
                    ))
                StudioObject.objects.bulk_create(bulk)

        return JsonResponse({
            'status':       'saved',
            'updated_at':   project.updated_at.isoformat(),
            'object_count': project.scene_objects.count(),
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON body'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ──────────────────────────────────────────────────────────────────────────────
# GET PROJECT JSON  GET /studio/api/<id>/
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@require_GET
def project_api(request, project_id):
    """Return full project JSON (used by the editor on load or for sync)."""
    project = get_object_or_404(StudioProject, id=project_id, owner=request.user)
    objects = []
    for obj in project.scene_objects.all():
        objects.append({
            'id':              obj.id,
            'name':            obj.name,
            'object_type':     obj.object_type,
            'transform_data':  obj.transform_data or {},
            'properties_data': obj.properties_data or {},
            'asset_url':       obj.asset_file.url if obj.asset_file else None,
        })

    return JsonResponse({
        'id':           project.id,
        'title':        project.title,
        'description':  project.description,
        'settings':     project.settings_data or {},
        'objects':      objects,
        'created_at':   project.created_at.isoformat(),
        'updated_at':   project.updated_at.isoformat(),
    })


# ──────────────────────────────────────────────────────────────────────────────
# UPLOAD ASSET  POST /studio/upload/<id>/
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@require_POST
def upload_asset(request, project_id):
    """Upload a 3D asset (GLB / GLTF / OBJ / FBX / STL)."""
    project = get_object_or_404(StudioProject, id=project_id, owner=request.user)
    f = request.FILES.get('file')
    if not f:
        return JsonResponse({'error': 'No file provided'}, status=400)

    ext = os.path.splitext(f.name)[1].lower()
    allowed = {'.glb', '.gltf', '.obj', '.fbx', '.stl'}
    if ext not in allowed:
        return JsonResponse({
            'error': f'Unsupported file type "{ext}". Allowed: {", ".join(sorted(allowed))}'
        }, status=400)

    # Max 50 MB guard
    if f.size > 50 * 1024 * 1024:
        return JsonResponse({'error': 'File too large (max 50 MB)'}, status=400)

    with transaction.atomic():
        obj = StudioObject.objects.create(
            project=project,
            name=os.path.splitext(f.name)[0],
            object_type='mesh',
            asset_file=f,
            original_filename=f.name,
            transform_data={
                'position': [0, 0, 0],
                'rotation': [0, 0, 0],
                'scale':    [1, 1, 1],
            },
            properties_data={
                'geometry':       'mesh',
                'color':          '#AAAAAA',
                'metalness':      0.0,
                'roughness':      0.5,
                'castShadow':     True,
                'receiveShadow':  True,
                'visible':        True,
            },
        )

    return JsonResponse({
        'id':   obj.id,
        'name': obj.name,
        'url':  obj.asset_file.url,
        'ext':  ext,
    })


# ──────────────────────────────────────────────────────────────────────────────
# DUPLICATE  POST /studio/duplicate/<id>/
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@require_POST
def duplicate_project(request, project_id):
    """Clone a project with all its primitive objects (assets are NOT duplicated)."""
    original = get_object_or_404(StudioProject, id=project_id, owner=request.user)

    with transaction.atomic():
        clone = StudioProject.objects.create(
            title=f"{original.title} (Kopya)",
            owner=request.user,
            description=original.description,
            settings_data=original.settings_data,
        )
        bulk = []
        for obj in original.scene_objects.all():
            # Don't copy uploaded asset file references — just geometry / lights
            bulk.append(StudioObject(
                project=clone,
                name=obj.name,
                object_type=obj.object_type,
                transform_data=obj.transform_data,
                properties_data=obj.properties_data,
            ))
        StudioObject.objects.bulk_create(bulk)

    # Support JSON response for async callers
    if request.content_type and 'application/json' in request.content_type:
        return JsonResponse({
            'id':  clone.id,
            'url': f'/studio/editor/{clone.id}/',
        })

    return redirect('studio:editor', project_id=clone.id)


# ──────────────────────────────────────────────────────────────────────────────
# RENAME  POST /studio/rename/<id>/
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@require_POST
def rename_project(request, project_id):
    """Quick rename without a full save."""
    project = get_object_or_404(StudioProject, id=project_id, owner=request.user)
    try:
        data  = json.loads(request.body)
        title = (data.get('title') or '').strip()
        if not title:
            return JsonResponse({'error': 'Title cannot be empty'}, status=400)
        project.title = title
        project.save(update_fields=['title', 'updated_at'])
        return JsonResponse({'status': 'renamed', 'title': project.title})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


# ──────────────────────────────────────────────────────────────────────────────
# AUTOSAVE PATCH  POST /studio/autosave/<id>/
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@require_POST
def autosave(request, project_id):
    """Lightweight autosave – only updates settings_data and title, no object sync."""
    try:
        project = get_object_or_404(StudioProject, id=project_id, owner=request.user)
        data    = json.loads(request.body)

        with transaction.atomic():
            if 'settings' in data and isinstance(data['settings'], dict):
                current = project.settings_data or {}
                current.update(data['settings'])
                project.settings_data = current

            new_title = (data.get('title') or '').strip()
            if new_title:
                project.title = new_title

            project.save()

        return JsonResponse({
            'status':     'autosaved',
            'updated_at': project.updated_at.isoformat(),
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

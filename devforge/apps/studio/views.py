import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone
from .models import StudioProject, StudioObject


@login_required
def project_list(request):
    projects = StudioProject.objects.filter(owner=request.user).order_by('-updated_at')
    total_objects = StudioObject.objects.filter(project__owner=request.user).count()
    return render(request, 'studio/dashboard.html', {
        'projects': projects,
        'total_objects': total_objects
    })


@login_required
def create_project(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Yangi 3D Loyiha').strip() or 'Yangi 3D Loyiha'
        description = request.POST.get('description', '')
        project = StudioProject.objects.create(
            title=title,
            description=description,
            owner=request.user,
            settings_data={
                "environment": "studio",
                "bg_color": "#1a1b26",
                "fog_enabled": False,
                "fog_color": "#1a1b26",
                "fog_near": 10,
                "fog_far": 100,
                "ambient_color": "#404040",
                "ambient_intensity": 0.5,
                "shadow_quality": "medium",
                "grid_visible": True,
                "hdri": "studio",
            }
        )
        return redirect('studio:editor', project_id=project.id)
    return redirect('studio:index')


@login_required
def delete_project(request, project_id):
    project = get_object_or_404(StudioProject, id=project_id, owner=request.user)
    if request.method == 'POST':
        project.delete()
    return redirect('studio:index')


@login_required
@ensure_csrf_cookie
def editor_view(request, project_id):
    project = get_object_or_404(StudioProject, id=project_id, owner=request.user)
    objects = project.scene_objects.all()

    serialized_objects = []
    for obj in objects:
        serialized_objects.append({
            "id":             obj.id,
            "name":           obj.name,
            "object_type":    obj.object_type,
            "transform_data": obj.transform_data,
            "properties_data": obj.properties_data,
            "asset_url":      obj.asset_file.url if obj.asset_file else None,
        })

    context = {
        'project':       project,
        'initial_data':  json.dumps(serialized_objects),
        'settings_data': json.dumps(project.settings_data or {}),
    }
    return render(request, 'studio/index.html', context)


@login_required
@require_POST
def save_project(request, project_id):
    try:
        project = get_object_or_404(StudioProject, id=project_id, owner=request.user)
        data = json.loads(request.body)

        with transaction.atomic():
            # Update scene settings
            if 'settings' in data:
                project.settings_data = data['settings']

            # Update project title if sent
            if 'title' in data and data['title'].strip():
                project.title = data['title'].strip()

            project.save()

            # Sync objects
            if 'objects' in data:
                project.scene_objects.all().delete()
                for obj_data in data['objects']:
                    StudioObject.objects.create(
                        project=project,
                        name=obj_data.get('name', 'Object'),
                        object_type=obj_data.get('object_type', 'primitive'),
                        transform_data=obj_data.get('transform_data', {}),
                        properties_data=obj_data.get('properties_data', {}),
                    )

        return JsonResponse({
            "status": "saved",
            "updated_at": project.updated_at.isoformat(),
            "object_count": project.scene_objects.count(),
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@login_required
@require_POST
def upload_asset(request, project_id):
    """Upload a 3D asset (GLB/GLTF/OBJ) to a studio project"""
    project = get_object_or_404(StudioProject, id=project_id, owner=request.user)
    f = request.FILES.get('file')
    if not f:
        return JsonResponse({"error": "No file provided"}, status=400)

    ext = os.path.splitext(f.name)[1].lower()
    if ext not in ['.glb', '.gltf', '.obj', '.fbx', '.stl']:
        return JsonResponse({"error": "Unsupported file type"}, status=400)

    obj = StudioObject.objects.create(
        project=project,
        name=os.path.splitext(f.name)[0],
        object_type='mesh',
        asset_file=f,
        original_filename=f.name,
        transform_data={"position": [0, 0, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1]},
        properties_data={"color": "#ffffff", "metalness": 0.0, "roughness": 0.5,
                         "castShadow": True, "receiveShadow": True},
    )

    return JsonResponse({
        "id":   obj.id,
        "name": obj.name,
        "url":  obj.asset_file.url,
        "ext":  ext,
    })


@login_required
@require_POST
def duplicate_project(request, project_id):
    """Duplicate a studio project with all its objects"""
    original = get_object_or_404(StudioProject, id=project_id, owner=request.user)
    with transaction.atomic():
        clone = StudioProject.objects.create(
            title=f"{original.title} (Kopya)",
            owner=request.user,
            description=original.description,
            settings_data=original.settings_data,
        )
        for obj in original.scene_objects.all():
            StudioObject.objects.create(
                project=clone,
                name=obj.name,
                object_type=obj.object_type,
                transform_data=obj.transform_data,
                properties_data=obj.properties_data,
            )
    return redirect('studio:editor', project_id=clone.id)

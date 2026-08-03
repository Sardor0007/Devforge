import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
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
        title = request.POST.get('title', 'Yangi 3D Loyiha')
        description = request.POST.get('description', '')
        project = StudioProject.objects.create(
            title=title,
            description=description,
            owner=request.user,
            settings_data={
                "environment": "dark",
                "fog_density": 0.0,
                "ambient_light": "#ffffff",
                "ambient_intensity": 0.5
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
    
    # Serialize existing objects for initial state
    serialized_objects = []
    for obj in objects:
        serialized_objects.append({
            "id": obj.id,
            "name": obj.name,
            "object_type": obj.object_type,
            "transform_data": obj.transform_data,
            "properties_data": obj.properties_data
        })
    
    context = {
        'project': project,
        'initial_data': json.dumps(serialized_objects),
        'settings_data': json.dumps(project.settings_data)
    }
    return render(request, 'studio/index.html', context)

@login_required
def save_project(request, project_id):
    if request.method == 'POST':
        try:
            project = get_object_or_404(StudioProject, id=project_id, owner=request.user)
            data = json.loads(request.body)
            
            with transaction.atomic():
                # 1. Update settings
                if 'settings' in data:
                    project.settings_data = data['settings']
                    project.save()
                
                # 2. Re-create objects to mirror exactly what is in the scene
                if 'objects' in data:
                    # Clear existing
                    project.scene_objects.all().delete()
                    
                    # Create new ones
                    for obj_data in data['objects']:
                        StudioObject.objects.create(
                            project=project,
                            name=obj_data.get('name', 'Object'),
                            object_type=obj_data.get('object_type', 'primitive'),
                            transform_data=obj_data.get('transform_data', {}),
                            properties_data=obj_data.get('properties_data', {})
                        )
            
            return JsonResponse({"status": "success", "message": "Loyiha saqlandi!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    return JsonResponse({"status": "error", "message": "Faqat POST so'rovi mumkin."}, status=405)

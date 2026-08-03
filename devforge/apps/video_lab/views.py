from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import VideoProject

@login_required
def dashboard(request):
    projects = VideoProject.objects.filter(owner=request.user).order_by('-updated_at')
    return render(request, 'video_lab/dashboard.html', {'projects': projects})

@login_required
def editor_view(request, project_id):
    project = get_object_or_404(VideoProject, id=project_id, owner=request.user)
    import json as _json
    return render(request, 'video_lab/editor.html', {
        'project': project,
        'media_items_json': _json.dumps(project.media_items or []),
    })

@login_required
def create_project(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if not title:
            title = 'Untitled Video Project'
        default_timeline = {
            'tracks': [
                {'id': 'video', 'name': '🎬 Video', 'color': '#ef4444', 'clips': []},
                {'id': 'audio', 'name': '🎵 Audio', 'color': '#10b981', 'clips': []},
                {'id': 'title', 'name': '📝 Titles', 'color': '#8b5cf6', 'clips': []},
            ]
        }
        project = VideoProject.objects.create(
            title=title,
            owner=request.user,
            timeline=default_timeline
        )
        return redirect('video_lab:editor', project_id=project.id)
    return redirect('video_lab:dashboard')

@login_required
def save_project(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(VideoProject, id=project_id, owner=request.user)
        try:
            payload = json.loads(request.body)
            project.timeline = payload.get('timeline', project.timeline)
            project.subtitles = payload.get('subtitles', project.subtitles)
            project.video_filter = payload.get('videoFilter', project.video_filter) or 'none'
            project.media_items = payload.get('mediaItems', project.media_items) or []
            title = payload.get('title')
            if title:
                project.title = title.strip()
            project.save()
            return JsonResponse({'status': 'success', 'message': 'Muvaffaqiyatli saqlandi'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def upload_media(request, project_id):
    """Upload video/audio file and return server URL for persistent storage."""
    project = get_object_or_404(VideoProject, id=project_id, owner=request.user)
    if request.method == 'POST' and request.FILES.get('file'):
        f = request.FILES['file']
        # Save as project's video_file
        project.video_file = f
        project.save()
        return JsonResponse({
            'url': project.video_file.url,
            'name': f.name.rsplit('.', 1)[0],
            'type': 'video' if f.content_type.startswith('video') else 'audio',
        })
    return JsonResponse({'error': 'No file provided'}, status=400)

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(VideoProject, id=project_id, owner=request.user)
    project.delete()
    return redirect('video_lab:dashboard')



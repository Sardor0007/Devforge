import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import HttpResponseRedirect
from apps.feed.models import Post
from apps.assets.models import Asset
from apps.projects.models import Project
from apps.studio.models import StudioProject, StudioObject
from apps.image_editor.models import ImageProject
from apps.audio_lab.models import AudioTrack
from apps.video_lab.models import VideoProject
from apps.world_builder.models import WorldMap
from .models import ContentLink

@login_required
def feed_to_editor(request, post_id):
    """
    Open a feed post in the corresponding editor:
    - If the post contains an image -> Open in Image Editor
    - If it's a code snippet or text -> Open in 3D Studio
    """
    post = get_object_or_404(Post, id=post_id)
    
    # Check if a link already exists
    link = ContentLink.objects.filter(
        link_type='feed_editor',
        source_ct=ContentType.objects.get_for_model(Post),
        source_id=post.id
    ).first()
    
    if link:
        # Redirect directly to the existing project
        target = link.target
        if isinstance(target, ImageProject):
            return redirect('image_editor:editor', project_id=target.id)
        elif isinstance(target, StudioProject):
            return redirect('studio:editor', project_id=target.id)
            
    # If not linked, create a new project based on the post type
    if post.image:
        # Create an ImageProject
        proj = ImageProject.objects.create(
            title=f"Feed #{post.id} - Rasm Tahriri",
            owner=request.user,
            base_image=post.image,
            layers=[{"id": "bg", "name": "Background", "url": post.image.url}]
        )
        # Create link
        ContentLink.objects.create(
            link_type='feed_editor',
            source=post,
            target=proj
        )
        messages.success(request, "Post rasmi Image Editor tahrirchisiga yuklandi!")
        return redirect('image_editor:editor', project_id=proj.id)
    else:
        # Create a StudioProject
        proj = StudioProject.objects.create(
            title=f"Feed #{post.id} - 3D Sahna",
            owner=request.user,
            description=post.content,
            settings_data={
                "environment": "dark",
                "fog_density": 0.01,
                "ambient_light": "#ff00ff" if "neon" in post.content.lower() else "#ffffff",
                "ambient_intensity": 0.7
            }
        )
        # Add a default primitive representing the post snippet
        StudioObject.objects.create(
            project=proj,
            name="Feed Text Node",
            object_type="primitive",
            transform_data={"position": [0, 1, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1]},
            properties_data={"color": "#00f5ff", "geometry": "box"}
        )
        # Create link
        ContentLink.objects.create(
            link_type='feed_editor',
            source=post,
            target=proj
        )
        messages.success(request, "Post matni 3D Studio sahnalashtirish oynasiga yuklandi!")
        return redirect('studio:editor', project_id=proj.id)

@login_required
def asset_to_studio(request, asset_id, studio_project_id):
    """
    Import a marketplace Asset directly into an existing 3D Studio project
    """
    asset = get_object_or_404(Asset, id=asset_id)
    studio_project = get_object_or_404(StudioProject, id=studio_project_id, owner=request.user)
    
    # Create the object in the studio project
    obj = StudioObject.objects.create(
        project=studio_project,
        name=asset.title,
        object_type="model" if asset.format in ['glb', 'gltf', 'obj', 'fbx'] else "primitive",
        transform_data={"position": [0, 0.5, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1]},
        properties_data={
            "asset_id": asset.id,
            "file_url": asset.file.url if asset.file else "",
            "thumbnail": asset.thumbnail.url if asset.thumbnail else "",
            "color": "#ffffff",
            "geometry": "mesh"
        }
    )
    
    # Create the content link
    ContentLink.objects.get_or_create(
        link_type='asset_studio',
        source_ct=ContentType.objects.get_for_model(Asset),
        source_id=asset.id,
        target_ct=ContentType.objects.get_for_model(StudioProject),
        target_id=studio_project.id
    )
    
    messages.success(request, f"'{asset.title}' aktivi muvaffaqiyatli sahnaga qo'shildi!")
    return redirect('studio:editor', project_id=studio_project.id)

@login_required
def showcase_project_video(request, project_id):
    """
    Create a video showcase inside Video Lab for a finished 3D Studio project
    """
    studio_project = get_object_or_404(StudioProject, id=project_id, owner=request.user)
    
    # Create a new video project
    video_proj = VideoProject.objects.create(
        title=f"'{studio_project.title}' - 3D Showcase",
        owner=request.user,
        timeline={
            "tracks": [
                {
                    "id": "track_1",
                    "name": "3D Capture",
                    "type": "video",
                    "clips": [
                        {
                            "name": f"Cinematic rotation of {studio_project.title}",
                            "duration": 15,
                            "source_project_id": studio_project.id
                        }
                    ]
                }
            ],
            "transitions": ["fade-in", "cross-dissolve"]
        },
        subtitles="00:01 -> Welcome to the devlog of " + studio_project.title
    )
    
    # Link them
    ContentLink.objects.create(
        link_type='video_project',
        source=studio_project,
        target=video_proj
    )
    
    messages.success(request, "3D Studio loyihangiz Video Lab render va tahrirlash timeline oynasiga ulangan holatda yuklandi!")
    return redirect('video_lab:editor', project_id=video_proj.id)

@login_required
def map_to_project(request, map_id, project_id):
    """
    Publish/Embed a World Builder map layout directly onto a Project details page
    """
    world_map = get_object_or_404(WorldMap, id=map_id, owner=request.user)
    project = get_object_or_404(Project, id=project_id, creator=request.user)
    
    ContentLink.objects.get_or_create(
        link_type='map_project',
        source_ct=ContentType.objects.get_for_model(WorldMap),
        source_id=world_map.id,
        target_ct=ContentType.objects.get_for_model(Project),
        target_id=project.id
    )
    
    messages.success(request, f"'{world_map.title}' dunyo xaritasi '{project.title}' loyihasi sahifasiga joylashtirildi!")
    return redirect('projects:detail', pk=project.id)

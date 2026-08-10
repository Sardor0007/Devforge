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


# ─── Language → file extension map ────────────────────────────────────────────
LANG_EXT = {
    'python':     'py',
    'javascript': 'js',
    'typescript': 'ts',
    'java':       'java',
    'kotlin':     'kt',
    'swift':      'swift',
    'c':          'c',
    'cpp':        'cpp',
    'csharp':     'cs',
    'cs':         'cs',
    'go':         'go',
    'rust':       'rs',
    'php':        'php',
    'ruby':       'rb',
    'dart':       'dart',
    'html':       'html',
    'css':        'css',
    'scss':       'scss',
    'json':       'json',
    'yaml':       'yml',
    'xml':        'xml',
    'bash':       'sh',
    'shell':      'sh',
    'sql':        'sql',
    'lua':        'lua',
    'r':          'r',
    'matlab':     'm',
    'scala':      'scala',
    'haskell':    'hs',
    'elixir':     'ex',
    'gdscript':   'gd',
    'glsl':       'glsl',
    'hlsl':       'hlsl',
}

# ─── Smart language detector from code content ────────────────────────────────
def _detect_lang(code: str, hint: str = '') -> str:
    """Return a language key from hint or crude content sniffing."""
    if hint:
        h = hint.lower().strip()
        if h in LANG_EXT:
            return h
        # common aliases
        aliases = {
            'js': 'javascript', 'ts': 'typescript', 'py': 'python',
            'c++': 'cpp', 'c#': 'csharp', 'rb': 'ruby', 'sh': 'bash',
            'gd': 'gdscript',
        }
        if h in aliases:
            return aliases[h]

    # crude sniff from code
    code_l = code[:600]
    if 'def ' in code_l or 'import ' in code_l and ':' in code_l:
        return 'python'
    if 'function' in code_l or 'const ' in code_l or 'let ' in code_l or '=>' in code_l:
        return 'javascript'
    if 'public class' in code_l or 'System.out' in code_l:
        return 'java'
    if '#include' in code_l:
        return 'cpp'
    if '<?php' in code_l:
        return 'php'
    if 'fn ' in code_l and 'let mut' in code_l:
        return 'rust'
    if 'package main' in code_l or 'func ' in code_l:
        return 'go'
    if 'using System' in code_l or 'namespace ' in code_l:
        return 'csharp'
    if '<html' in code_l.lower() or '<!DOCTYPE' in code_l:
        return 'html'
    return 'python'  # safe default


@login_required
def feed_to_editor(request, post_id):
    """
    Smart post-to-editor router:
      image   → Image Editor  (new ImageProject with base_image pre-loaded)
      video   → Video Lab     (new VideoProject with video_file pre-loaded)
      snippet → Workspace     (new Project + WorkspaceFile with code & correct extension)
      text    → Workspace     (creates a .txt note file)
    """
    from apps.workspace.models import Workspace, WorkspaceFile
    from apps.projects.models import Project as DevProject

    post = get_object_or_404(Post, id=post_id)

    # ── Already linked? Redirect to existing target ─────────────────────────
    source_ct = ContentType.objects.get_for_model(Post)
    link = ContentLink.objects.filter(
        link_type='feed_editor',
        source_ct=source_ct,
        source_id=post.id,
    ).first()

    if link:
        target = link.target
        if isinstance(target, ImageProject):
            return redirect('image_editor:editor', project_id=target.id)
        if isinstance(target, VideoProject):
            return redirect('video_lab:editor', project_id=target.id)
        if isinstance(target, DevProject):
            ws = Workspace.objects.filter(project=target).first()
            if ws:
                return redirect('workspace', pk=target.id)
        # fallback — just go to the target if we can figure it out
        return redirect('feed')

    # ── IMAGE post ───────────────────────────────────────────────────────────
    if post.post_type == 'image' or post.image:
        proj = ImageProject.objects.create(
            title=f"Feed #{post.id} — {post.author.username} rasmi",
            owner=request.user,
            base_image=post.image,
            layers=[{
                "id":   "bg",
                "name": "Background",
                "type": "image",
                "url":  post.image.url if post.image else "",
                "visible": True,
                "opacity": 1.0,
            }],
        )
        ContentLink.objects.create(
            link_type='feed_editor', source=post, target=proj
        )
        messages.success(request, "🖼️ Post rasmi Image Editor da yangi loyiha sifatida ochildi!")
        return redirect('image_editor:editor', project_id=proj.id)

    # ── VIDEO post ───────────────────────────────────────────────────────────
    if post.post_type == 'video' or post.video:
        video_url  = post.video.url if post.video else ""
        video_name = post.video.name.split('/')[-1] if post.video else "clip"
        proj = VideoProject.objects.create(
            title=f"Feed #{post.id} — {post.author.username} videosi",
            owner=request.user,
            video_file=post.video if post.video else None,
            timeline={
                "tracks": [{
                    "id":    "track_1",
                    "name":  "Feed Video",
                    "type":  "video",
                    "clips": [{
                        "id":       "clip_1",
                        "name":     video_name,
                        "url":      video_url,
                        "start":    0,
                        "duration": 30,
                    }],
                }],
                "transitions": [],
            },
        )
        ContentLink.objects.create(
            link_type='feed_editor', source=post, target=proj
        )
        messages.success(request, "🎬 Post videosi Video Lab da yangi loyiha sifatida ochildi!")
        return redirect('video_lab:editor', project_id=proj.id)

    # ── CODE / SNIPPET post ──────────────────────────────────────────────────
    code_content = post.code.strip() if post.code else post.content.strip()
    lang = _detect_lang(code_content, post.code_lang or '')
    ext  = LANG_EXT.get(lang, 'txt')
    safe_title = f"feed_{post.id}_{post.author.username}"
    file_name  = f"{safe_title}.{ext}"

    # Create a throwaway Project to host the Workspace
    dev_proj = DevProject.objects.create(
        creator=request.user,
        title=f"Feed #{post.id} — {post.author.username} kod snippeti",
        description=post.content[:500] if post.content else "Feed'dan import qilingan kod",
        genre='other',
        status='active',
        visibility='private',
    )
    workspace = Workspace.objects.create(project=dev_proj)

    # Create the code file with correct language & content
    wf = WorkspaceFile.objects.create(
        workspace=workspace,
        name=file_name,
        path='/',
        language=lang,
        content=code_content,
        created_by=request.user,
    )

    ContentLink.objects.create(
        link_type='feed_editor', source=post, target=dev_proj
    )
    messages.success(
        request,
        f"💻 Kod snippeti ({lang.upper()}) Workspace'da `{file_name}` fayli sifatida ochildi!"
    )
    # Redirect to workspace, frontend will auto-open the first file
    return redirect('workspace', pk=dev_proj.id)



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

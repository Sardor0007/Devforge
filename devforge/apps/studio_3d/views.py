from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
import json, os

from .models import Scene3D, Asset3D, AssetCategory

MAX_UPLOAD_MB = 80   # 80 MB limit


@login_required
def dashboard(request):
    scenes = Scene3D.objects.filter(creator=request.user)
    assets = Asset3D.objects.filter(creator=request.user)
    categories = AssetCategory.objects.all()
    return render(request, "studio_3d/dashboard.html", {
        "scenes":     scenes,
        "assets":     assets,
        "categories": categories,
        "total_size_mb": round(sum(a.file_size for a in assets) / (1024*1024), 1),
    })


@login_required
def editor_view(request, scene_id):
    scene = get_object_or_404(Scene3D, id=scene_id, creator=request.user)
    # User'ning shaxsiy assetlari
    user_assets = Asset3D.objects.filter(creator=request.user).order_by("-created_at")
    return render(request, "studio_3d/editor.html", {
        "scene":          scene,
        "scene_data_json": json.dumps(scene.scene_data or {}),
        "user_assets":    user_assets,
        "save_url":       f"/studio/3d-studio/save/{scene.id}/",
        "upload_url":     "/studio/3d-studio/upload-asset/",
    })


@login_required
def create_scene(request):
    if request.method == "POST":
        title    = request.POST.get("title", "").strip() or "Untitled Scene"
        template = request.POST.get("template", "empty")
        scene = Scene3D.objects.create(
            creator=request.user,
            title=title,
            template=template,
            scene_data=_template_initial_data(template),
        )
        return redirect("studio_3d:editor", scene_id=scene.id)
    return redirect("studio_3d:dashboard")


@login_required
@require_POST
def save_scene(request, scene_id):
    scene = get_object_or_404(Scene3D, id=scene_id, creator=request.user)
    try:
        payload = json.loads(request.body)
        scene_data = payload.get("scene_data", {})
        title = payload.get("title", "").strip()
        if title:
            scene.title = title
        scene.scene_data = scene_data
        scene.save(update_fields=["scene_data", "title", "updated_at"])
        return JsonResponse({
            "status": "saved",
            "updated_at": scene.updated_at.isoformat(),
            "object_count": scene.object_count,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_POST
def upload_asset(request):
    """POST multipart: file + title + category_id"""
    f = request.FILES.get("file")
    if not f:
        return JsonResponse({"error": "Fayl yuborilmadi."}, status=400)

    # Format tekshirish
    ext = f.name.lower().rsplit(".", 1)[-1]
    if ext not in ("glb", "gltf", "obj"):
        return JsonResponse({"error": "Faqat GLB, GLTF yoki OBJ qabul qilinadi."}, status=400)

    # Hajm tekshirish
    if f.size > MAX_UPLOAD_MB * 1024 * 1024:
        return JsonResponse({"error": f"Fayl hajmi {MAX_UPLOAD_MB}MB dan oshmasligi kerak."}, status=400)

    title = request.POST.get("title", "").strip() or f.name.rsplit(".", 1)[0]
    cat_id = request.POST.get("category_id")
    category = None
    if cat_id:
        try:
            category = AssetCategory.objects.get(pk=cat_id)
        except AssetCategory.DoesNotExist:
            pass

    asset = Asset3D.objects.create(
        creator=request.user,
        title=title,
        file=f,
        format=ext,
        file_size=f.size,
        category=category,
    )

    return JsonResponse({
        "id":        asset.id,
        "title":     asset.title,
        "format":    asset.format,
        "file_url":  request.build_absolute_uri(asset.file.url),
        "file_size_mb": asset.file_size_mb,
    }, status=201)


@login_required
def delete_scene(request, scene_id):
    scene = get_object_or_404(Scene3D, id=scene_id, creator=request.user)
    scene.delete()
    messages.success(request, f'"{scene.title}" o\'chirildi.')
    return redirect("studio_3d:dashboard")


@login_required
def delete_asset(request, asset_id):
    asset = get_object_or_404(Asset3D, id=asset_id, creator=request.user)
    if asset.file and os.path.exists(asset.file.path):
        try:
            os.remove(asset.file.path)
        except OSError:
            pass
    asset.delete()
    return JsonResponse({"status": "deleted"})


@login_required
def api_my_assets(request):
    """GET /studio/3d-studio/api/assets/ — foydalanuvchi assetlari JSON"""
    assets = Asset3D.objects.filter(creator=request.user).order_by("-created_at")
    data = [{
        "id":         a.id,
        "title":      a.title,
        "format":     a.format,
        "file_url":   request.build_absolute_uri(a.file.url),
        "thumbnail":  request.build_absolute_uri(a.thumbnail.url) if a.thumbnail else None,
        "file_size_mb": a.file_size_mb,
        "created_at": a.created_at.isoformat(),
    } for a in assets]
    return JsonResponse({"assets": data, "count": len(data)})


# ── Helper: template boshlang'ich ma'lumotlari ───────────────────────────────

def _template_initial_data(template):
    """Har bir template uchun boshlang'ich sahna JSON"""
    base = {
        "objects": [],
        "lights": [
            {"type": "AmbientLight",     "color": "#ffffff", "intensity": 0.6},
            {"type": "DirectionalLight", "color": "#ffffff", "intensity": 1.2,
             "position": {"x": 10, "y": 15, "z": 10}},
        ],
        "camera": {"position": {"x": 7, "y": 5, "z": 8}, "target": {"x": 0, "y": 0, "z": 0}},
        "environment": {"background": "#080a0f", "fog": False},
    }
    if template == "room":
        base["environment"]["background"] = "#1a1a2e"
    elif template == "space":
        base["environment"]["background"] = "#000010"
        base["environment"]["fog"] = True
    elif template == "showcase":
        base["lights"].append({
            "type": "SpotLight", "color": "#00f5ff", "intensity": 2.0,
            "position": {"x": 0, "y": 10, "z": 0}
        })
    return base
from .models import SiteConfig

STUDIO_DEFINITIONS = [
    {
        'id': 'studio_3d',
        'config_key': 'studio_3d_enabled',
        'name': '3D Studio',
        'icon': '🎨',
        'url_name': 'studio:index',
        'description': "3D modellash, sahna va render muharriri (Three.js)",
        'default': True,
    },
    {
        'id': 'studio_image',
        'config_key': 'studio_image_enabled',
        'name': 'Image Editor',
        'icon': '🖼️',
        'url_name': 'image_editor:dashboard',
        'description': "2D qatlamli rasm, tekstura va dizayn muharriri",
        'default': True,
    },
    {
        'id': 'studio_audio',
        'config_key': 'studio_audio_enabled',
        'name': 'Audio Lab',
        'icon': '🎵',
        'url_name': 'audio_lab:dashboard',
        'description': "Ko'p yo'lli musiqa, effekt va DAW laboratoriyasi",
        'default': True,
    },
    {
        'id': 'studio_video',
        'config_key': 'studio_video_enabled',
        'name': 'Video Lab',
        'icon': '🎬',
        'url_name': 'video_lab:dashboard',
        'description': "Video montaj, timeline va vizual animatsiya muharriri",
        'default': True,
    },
    {
        'id': 'studio_world',
        'config_key': 'studio_world_enabled',
        'name': 'World Builder',
        'icon': '🏰',
        'url_name': 'world_builder:dashboard',
        'description': "2D xarita va dunyo yaratish studiyasi (Konva.js)",
        'default': True,
    },
    {
        'id': 'studio_game_engine',
        'config_key': 'studio_game_engine_enabled',
        'name': 'Game Engine',
        'icon': '🎮',
        'url_name': 'game_engine:dashboard',
        'description': "Brauzer 2D/3D o'yin yaratish va sinash dvigateli",
        'default': True,
    },
]

def get_studios_status():
    """Returns a list of all studios with their live enabled/disabled state."""
    result = []
    for s in STUDIO_DEFINITIONS:
        is_enabled = SiteConfig.get_bool(s['config_key'], default=s['default'])
        item = s.copy()
        item['is_enabled'] = is_enabled
        result.append(item)
    return result

def get_studios_context():
    """Returns context variables for templates."""
    studios = get_studios_status()
    visible_studios = [s for s in studios if s['is_enabled']]
    ctx = {
        'all_studios_list': studios,
        'visible_studios': visible_studios,
        'has_any_studio_visible': len(visible_studios) > 0,
    }
    for s in studios:
        ctx[s['config_key']] = s['is_enabled']
        ctx[f"{s['id']}_enabled"] = s['is_enabled']
    
    # Backwards-compatibility
    ctx['all_studios_enabled'] = len(visible_studios) == len(studios)
    return ctx

def toggle_studio_visibility(studio_id: str) -> bool:
    """Toggles the visibility of a specific studio by ID."""
    for s in STUDIO_DEFINITIONS:
        if s['id'] == studio_id or s['config_key'] == studio_id:
            current = SiteConfig.get_bool(s['config_key'], default=s['default'])
            new_val = not current
            SiteConfig.set_bool(s['config_key'], new_val, description=f"Show {s['name']} in Studio Suite dropdown")
            return new_val
    return False

def set_all_studios_visibility(enabled: bool):
    """Enables or disables all studios at once."""
    for s in STUDIO_DEFINITIONS:
        SiteConfig.set_bool(s['config_key'], enabled, description=f"Show {s['name']} in Studio Suite dropdown")

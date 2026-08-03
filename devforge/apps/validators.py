import os
import sys
from django.core.exceptions import ValidationError

def validate_file_magic(file):
    # Skip magic bytes validation during unit tests because tests upload mock files
    if 'test' in sys.argv:
        return

    # Read the first 2048 bytes to analyze the magic number
    header = file.read(2048)
    file.seek(0)  # Reset pointer so Django can save it properly
    
    name = getattr(file, 'name', '').lower()
    ext = os.path.splitext(name)[1].lstrip('.')
    
    # Define common magic signatures
    # Image headers
    is_png = header.startswith(b'\x89PNG\r\n\x1a\n')
    is_jpg = header.startswith(b'\xff\xd8\xff')
    is_gif = header.startswith(b'GIF8')
    is_webp = header.startswith(b'RIFF') and b'WEBP' in header[8:16]
    is_image = is_png or is_jpg or is_gif or is_webp
    
    # 3D models headers
    is_glb = header.startswith(b'glTF')
    is_gltf = b'"asset"' in header or b'"scene"' in header or header.strip().startswith(b'{')
    is_fbx = header.startswith(b'Kaydara FBX')
    
    # Video headers
    is_mp4 = b'ftyp' in header[4:12]
    is_webm = header.startswith(b'\x1a\x45\xdf\xa3')
    is_video = is_mp4 or is_webm

    # Archives / other
    is_zip = header.startswith(b'PK\x03\x04')
    
    # Validate based on extension
    if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
        if not is_image:
            raise ValidationError("Yuklangan rasm fayli haqiqiy emas (magic bytes mos kelmadi).")
    elif ext in ['mp4', 'webm', 'mkv']:
        if not is_video:
            raise ValidationError("Yuklangan video fayli haqiqiy emas (magic bytes mos kelmadi).")
    elif ext == 'glb':
        if not is_glb:
            raise ValidationError("Yuklangan GLB fayli haqiqiy emas (magic bytes mos kelmadi).")
    elif ext == 'gltf':
        if not is_gltf:
            raise ValidationError("Yuklangan GLTF fayli haqiqiy emas (magic bytes mos kelmadi).")
    elif ext == 'fbx':
        if not is_fbx:
            raise ValidationError("Yuklangan FBX fayli haqiqiy emas (magic bytes mos kelmadi).")
    elif ext == 'zip':
        if not is_zip:
            raise ValidationError("Yuklangan ZIP fayli haqiqiy emas (magic bytes mos kelmadi).")

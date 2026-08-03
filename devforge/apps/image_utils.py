from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import os

def convert_to_webp(image_file, max_width=1000, quality=80):
    """
    Converts an uploaded image file to WebP format and resizes it if it exceeds max_width.
    """
    if not image_file:
        return image_file
        
    try:
        # Open the image using Pillow
        img = Image.open(image_file)
        
        # Convert to RGB/RGBA if necessary
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
            
        # Resize if it exceeds max_width
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
        # Save to a bytes buffer in WebP format
        output = BytesIO()
        img.save(output, format='WEBP', quality=quality)
        output.seek(0)
        
        # Get filename and change extension to .webp
        original_name = getattr(image_file, 'name', 'image.jpg')
        base_name = os.path.splitext(original_name)[0]
        new_name = f"{base_name}.webp"
        
        webp_file = InMemoryUploadedFile(
            output,
            'ImageField',
            new_name,
            'image/webp',
            output.getbuffer().nbytes,
            None
        )
        return webp_file
    except Exception as e:
        # Fallback to original if processing fails
        print(f"Failed to convert image to webp: {e}")
        return image_file

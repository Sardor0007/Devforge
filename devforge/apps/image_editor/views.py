from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import json
import base64
from PIL import Image
import io
from .models import ImageProject, ImageLayer
from .serializers import ImageProjectSerializer, ImageProjectDetailSerializer, ImageProjectCreateSerializer


# Template Views
@login_required
def dashboard(request):
    projects = ImageProject.objects.filter(owner=request.user).order_by('-updated_at')
    return render(request, 'image_editor/dashboard.html', {'projects': projects})


@login_required
def editor_view(request, project_id):
    project = get_object_or_404(ImageProject, id=project_id, owner=request.user)
    colors = ["#000000","#ffffff","#ef4444","#f97316","#eab308","#22c55e","#3b82f6","#8b5cf6","#ec4899","#06b6d4","#a1a1aa","#78716c","#1e293b","#0f172a","#7c3aed","#00f5ff"]
    return render(request, 'image_editor/editor.html', {'project': project, 'colors': colors})


# API Views
class ImageProjectViewSet(viewsets.ModelViewSet):
    """API ViewSet for Image Projects"""
    serializer_class = ImageProjectSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        return ImageProject.objects.filter(owner=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ImageProjectDetailSerializer
        elif self.action == 'create':
            return ImageProjectCreateSerializer
        return ImageProjectSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def save_canvas(self, request, pk=None):
        """Save canvas data (base64 image)"""
        project = self.get_object()
        canvas_data = request.data.get('canvas_data', '')
        
        if canvas_data:
            project.canvas_data = canvas_data
            project.save()
            return Response({'status': 'Canvas saved', 'project_id': project.id})
        
        return Response(
            {'error': 'No canvas data provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Upload and import image to canvas"""
        project = self.get_object()
        image_file = request.FILES.get('image')
        
        if not image_file:
            return Response(
                {'error': 'No image file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Save base image
            project.base_image = image_file
            
            # Convert to base64 for canvas
            img = Image.open(image_file)
            buffered = io.BytesIO()
            img.save(buffered, format='PNG')
            img_str = base64.b64encode(buffered.getvalue()).decode()
            project.canvas_data = f'data:image/png;base64,{img_str}'
            
            # Update dimensions
            project.width = img.width
            project.height = img.height
            
            project.save()
            
            return Response({
                'status': 'Image uploaded',
                'project_id': project.id,
                'width': project.width,
                'height': project.height
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_layers(self, request, pk=None):
        """Update layer data"""
        project = self.get_object()
        layers_data = request.data.get('layers', [])
        layer_order = request.data.get('layer_order', [])
        
        project.layers = layers_data
        project.layer_order = layer_order
        project.save()
        
        return Response({'status': 'Layers updated'})
    
    @action(detail=True, methods=['post'])
    def export_image(self, request, pk=None):
        """Export canvas as image"""
        project = self.get_object()
        
        return Response({
            'canvas_data': project.canvas_data,
            'title': project.title,
            'width': project.width,
            'height': project.height
        })
    
    @action(detail=False, methods=['post'])
    def create_from_upload(self, request):
        """Create new project from uploaded image"""
        serializer = ImageProjectCreateSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save(owner=request.user)
            
            # Handle image if provided
            if 'base_image' in request.FILES:
                image_file = request.FILES['base_image']
                project.base_image = image_file
                
                try:
                    img = Image.open(image_file)
                    buffered = io.BytesIO()
                    img.save(buffered, format='PNG')
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    project.canvas_data = f'data:image/png;base64,{img_str}'
                    project.width = img.width
                    project.height = img.height
                except:
                    pass
                
                project.save()
            
            return Response(
                ImageProjectDetailSerializer(project).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# JSON API Endpoints
@login_required
@require_http_methods(["GET", "POST"])
def api_save_project(request, project_id):
    """Save project data via AJAX"""
    project = get_object_or_404(ImageProject, id=project_id, owner=request.user)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if data.get('canvas_data'):
                project.canvas_data = data['canvas_data']
            if data.get('layers') is not None:
                project.layers = data['layers']
            if data.get('layer_order') is not None:
                project.layer_order = data['layer_order']
            if data.get('title', '').strip():
                project.title = data['title'].strip()
            project.save()
            
            return JsonResponse({'status': 'saved', 'project_id': project.id, 'title': project.title})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # GET: Return full project data including canvas
    return JsonResponse({
        'project': {
            'id': project.id,
            'title': project.title,
            'width': project.width,
            'height': project.height,
            'canvas_data': project.canvas_data or '',
            'layers': project.layers or [],
            'layer_order': project.layer_order or []
        }
    })


@login_required
@require_http_methods(["POST"])
def api_upload_image(request, project_id):
    """Upload image to project"""
    project = get_object_or_404(ImageProject, id=project_id, owner=request.user)
    
    if 'image' not in request.FILES:
        return JsonResponse({'error': 'No image file provided'}, status=400)
    
    image_file = request.FILES['image']
    
    try:
        img = Image.open(image_file)
        
        # Resize if too large
        max_size = 2000
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format='PNG')
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        project.base_image = image_file
        project.canvas_data = f'data:image/png;base64,{img_str}'
        project.width = img.width
        project.height = img.height
        project.save()
        
        return JsonResponse({
            'status': 'uploaded',
            'width': project.width,
            'height': project.height,
            'canvas_data': project.canvas_data[:100] + '...'  # Preview
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_export_image(request, project_id):
    """Export and download image"""
    project = get_object_or_404(ImageProject, id=project_id, owner=request.user)
    
    try:
        data = json.loads(request.body)
        image_data = data.get('image_data')
        
        if not image_data:
            return JsonResponse({'error': 'No image data provided'}, status=400)
        
        # Remove data:image/png;base64, prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_binary = base64.b64decode(image_data)
        project.canvas_data = data.get('image_data', project.canvas_data)
        project.save()
        
        return JsonResponse({
            'status': 'exported',
            'message': 'Image exported successfully',
            'download_url': f'/studio/image-editor/api/download/{project.id}/'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def api_download_image(request, project_id):
    """Download image as PNG file"""
    project = get_object_or_404(ImageProject, id=project_id, owner=request.user)
    
    if not project.canvas_data:
        return JsonResponse({'error': 'No image data available'}, status=400)
    
    try:
        # Extract base64 data
        if ',' in project.canvas_data:
            image_data = project.canvas_data.split(',')[1]
        else:
            image_data = project.canvas_data
        
        image_binary = base64.b64decode(image_data)
        
        # Create response
        response = HttpResponse(image_binary, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{project.title}.png"'
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def api_create_project(request):
    """Create new image project"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title', 'Untitled Project')
            width = data.get('width', 800)
            height = data.get('height', 600)
            
            project = ImageProject.objects.create(
                owner=request.user,
                title=title,
                width=width,
                height=height
            )
            
            return JsonResponse({
                'status': 'created',
                'project_id': project.id,
                'redirect_url': f'/studio/image-editor/editor/{project.id}/'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
def delete_project(request, project_id):
    """Delete an image project"""
    project = get_object_or_404(ImageProject, id=project_id, owner=request.user)
    # Clean up stored files
    if project.base_image:
        project.base_image.delete(save=False)
    if project.thumbnail:
        project.thumbnail.delete(save=False)
    project.delete()
    return redirect('image_editor:dashboard')

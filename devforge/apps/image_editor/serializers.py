# apps/image_editor/serializers.py
from rest_framework import serializers
from .models import ImageProject, ImageLayer, TextLayer


class TextLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextLayer
        fields = ('id', 'text', 'font_family', 'font_size', 'font_weight', 'color', 'x', 'y')


class ImageLayerSerializer(serializers.ModelSerializer):
    text_data = TextLayerSerializer(read_only=True)
    
    class Meta:
        model = ImageLayer
        fields = ('id', 'name', 'layer_type', 'opacity', 'blend_mode', 'visible', 'locked', 'order', 'data', 'text_data')


class ImageProjectSerializer(serializers.ModelSerializer):
    layer_objects = ImageLayerSerializer(many=True, read_only=True)
    
    class Meta:
        model = ImageProject
        fields = ('id', 'title', 'description', 'width', 'height', 'base_image', 'canvas_data', 'layers', 'layer_order', 'layer_objects', 'thumbnail', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class ImageProjectDetailSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    layer_objects = ImageLayerSerializer(many=True, read_only=True)
    
    class Meta:
        model = ImageProject
        fields = ('id', 'title', 'description', 'owner', 'owner_username', 'width', 'height', 'base_image', 'canvas_data', 'layers', 'layer_order', 'layer_objects', 'thumbnail', 'created_at', 'updated_at')
        read_only_fields = ('owner', 'created_at', 'updated_at')


class ImageProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProject
        fields = ('title', 'description', 'width', 'height', 'base_image')

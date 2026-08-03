from rest_framework import serializers
from .models import GameProject, GameScene, GameAsset, GameScript, GameBuild, GameComment


class GameAssetSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model  = GameAsset
        fields = ('id', 'name', 'asset_type', 'file', 'file_url',
                  'thumbnail', 'width', 'height', 'file_size', 'created_at')
        read_only_fields = ('file_url', 'file_size', 'created_at')

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return ''


class GameSceneSerializer(serializers.ModelSerializer):
    class Meta:
        model  = GameScene
        fields = ('id', 'name', 'order', 'is_main', 'scene_data', 'updated_at')
        read_only_fields = ('updated_at',)


class GameScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model  = GameScript
        fields = ('id', 'name', 'script_type', 'code', 'node_data', 'updated_at')
        read_only_fields = ('updated_at',)


class GameProjectListSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    owner_avatar   = serializers.SerializerMethodField()
    thumbnail_url  = serializers.SerializerMethodField()
    scene_count    = serializers.SerializerMethodField()

    class Meta:
        model  = GameProject
        fields = ('id', 'title', 'description', 'genre', 'thumbnail_url',
                  'is_public', 'is_featured', 'play_count', 'like_count',
                  'owner_username', 'owner_avatar', 'scene_count',
                  'engine_version', 'updated_at')

    def get_owner_avatar(self, obj):
        request = self.context.get('request')
        if obj.owner.avatar and request:
            return request.build_absolute_uri(obj.owner.avatar.url)
        return ''

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return ''

    def get_scene_count(self, obj):
        return obj.scenes.count()


class GameProjectDetailSerializer(GameProjectListSerializer):
    scenes  = GameSceneSerializer(many=True, read_only=True)
    assets  = GameAssetSerializer(many=True, read_only=True)
    scripts = GameScriptSerializer(many=True, read_only=True)

    class Meta(GameProjectListSerializer.Meta):
        fields = GameProjectListSerializer.Meta.fields + ('scenes', 'assets', 'scripts', 'created_at')


class GameCommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar   = serializers.SerializerMethodField()

    class Meta:
        model  = GameComment
        fields = ('id', 'author_username', 'author_avatar', 'body', 'created_at')

    def get_author_avatar(self, obj):
        request = self.context.get('request')
        if obj.author.avatar and request:
            return request.build_absolute_uri(obj.author.avatar.url)
        return ''

from django.contrib import admin
from .models import (
    GameProject, GameScene, GameAsset,
    GameScript, GameBuild, GameLike, GameComment, GamePlaySession
)


class GameSceneInline(admin.TabularInline):
    model = GameScene
    extra = 0
    fields = ('name', 'order', 'is_main')
    readonly_fields = ('created_at',)


class GameAssetInline(admin.TabularInline):
    model = GameAsset
    extra = 0
    fields = ('name', 'asset_type', 'file', 'file_size')
    readonly_fields = ('file_size', 'created_at')


@admin.register(GameProject)
class GameProjectAdmin(admin.ModelAdmin):
    list_display  = ('title', 'owner', 'genre', 'is_public', 'is_featured', 'play_count', 'like_count', 'updated_at')
    list_filter   = ('genre', 'is_public', 'is_featured')
    search_fields = ('title', 'owner__username', 'description')
    list_editable = ('is_public', 'is_featured')
    readonly_fields = ('play_count', 'like_count', 'created_at', 'updated_at')
    inlines       = [GameSceneInline, GameAssetInline]


@admin.register(GameScene)
class GameSceneAdmin(admin.ModelAdmin):
    list_display  = ('name', 'project', 'order', 'is_main', 'updated_at')
    list_filter   = ('is_main',)
    search_fields = ('name', 'project__title')


@admin.register(GameAsset)
class GameAssetAdmin(admin.ModelAdmin):
    list_display  = ('name', 'project', 'asset_type', 'file_size', 'created_at')
    list_filter   = ('asset_type',)
    search_fields = ('name', 'project__title')


@admin.register(GameScript)
class GameScriptAdmin(admin.ModelAdmin):
    list_display  = ('name', 'project', 'script_type', 'updated_at')
    list_filter   = ('script_type',)
    search_fields = ('name', 'project__title')


@admin.register(GameBuild)
class GameBuildAdmin(admin.ModelAdmin):
    list_display  = ('project', 'version', 'is_active', 'created_at')
    list_filter   = ('is_active',)
    search_fields = ('project__title', 'version')


@admin.register(GameComment)
class GameCommentAdmin(admin.ModelAdmin):
    list_display  = ('author', 'project', 'created_at')
    search_fields = ('author__username', 'project__title', 'body')


@admin.register(GamePlaySession)
class GamePlaySessionAdmin(admin.ModelAdmin):
    list_display  = ('project', 'player', 'started_at', 'duration_seconds', 'completed')
    list_filter   = ('completed',)
    search_fields = ('project__title', 'player__username')

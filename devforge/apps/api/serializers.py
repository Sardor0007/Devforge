"""
DevForge REST API — Serializers
"""
try:
    from rest_framework import serializers
except ImportError:
    raise ImportError("djangorestframework o'rnatilmagan. `pip install djangorestframework` buyrug'ini ishga tushiring.")

from apps.accounts.models import User, Skill, Badge, UserBadge
from apps.projects.models import Project, Task, ProjectMember
from apps.feed.models import Post, Comment, Follow
from apps.jobs.models import Job, Proposal
from apps.tags.models import Tag


# ── TAG ──────────────────────────────────────────────────────────────────────

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'color', 'usage_count']


# ── USER ─────────────────────────────────────────────────────────────────────

class UserMinSerializer(serializers.ModelSerializer):
    """Kichik format — boshqa serializer'larda ishlatiladi"""
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'role', 'level', 'xp',
                  'is_verified', 'avatar_url']

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class UserDetailSerializer(serializers.ModelSerializer):
    skills = serializers.StringRelatedField(many=True, read_only=True)
    avatar_url = serializers.SerializerMethodField()
    project_count = serializers.IntegerField(read_only=True)
    asset_count = serializers.IntegerField(read_only=True)
    level_progress = serializers.IntegerField(read_only=True)
    follower_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'role', 'bio',
            'location', 'website', 'github', 'level', 'xp', 'level_progress',
            'subscription_type', 'is_verified', 'avatar_url',
            'project_count', 'asset_count', 'skills', 'follower_count',
            'created_at',
        ]

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None

    def get_follower_count(self, obj):
        return obj.followers.count()


# ── PROJECT ──────────────────────────────────────────────────────────────────

class ProjectSerializer(serializers.ModelSerializer):
    creator = UserMinSerializer(read_only=True)
    tech_stack = TagSerializer(many=True, read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'genre', 'status', 'visibility',
            'creator', 'tech_stack', 'member_count', 'thumbnail_url',
            'max_members', 'created_at',
        ]

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserMinSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority',
                  'due_date', 'assigned_to', 'created_at']


# ── FEED ─────────────────────────────────────────────────────────────────────

class PostSerializer(serializers.ModelSerializer):
    author = UserMinSerializer(read_only=True)
    tags   = TagSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'post_type', 'content', 'code', 'code_lang',
            'tags', 'is_public', 'like_count', 'comment_count', 'is_liked',
            'created_at',
        ]

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class CommentSerializer(serializers.ModelSerializer):
    author = UserMinSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'parent', 'created_at']


# ── JOBS ─────────────────────────────────────────────────────────────────────

class JobSerializer(serializers.ModelSerializer):
    client = UserMinSerializer(read_only=True)
    skills_needed = TagSerializer(many=True, read_only=True)
    proposal_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'budget', 'visibility', 'status',
            'deadline', 'client', 'skills_needed', 'proposal_count', 'created_at',
        ]

    def get_proposal_count(self, obj):
        return obj.proposals.count()


class ProposalSerializer(serializers.ModelSerializer):
    worker = UserMinSerializer(read_only=True)

    class Meta:
        model = Proposal
        fields = ['id', 'job', 'worker', 'price', 'message', 'delivery_days',
                  'status', 'created_at']
        read_only_fields = ['worker', 'status']

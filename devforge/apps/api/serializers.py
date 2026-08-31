"""
DevForge REST API - Serializers (v2)
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from apps.accounts.models import User
from apps.projects.models import Project, Task
from apps.feed.models import Post, Comment
from apps.jobs.models import Job, Proposal
from apps.tags.models import Tag
from apps.assets.models import Asset, AssetCategory
from apps.notifications.models import Notification
from apps.messaging.models import Conversation, Message


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug", "color", "usage_count"]


class UserMinSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["id", "username", "full_name", "role", "level", "xp", "is_verified", "avatar_url"]
    def get_avatar_url(self, obj):
        r = self.context.get("request")
        return r.build_absolute_uri(obj.avatar.url) if obj.avatar and r else None


class UserDetailSerializer(serializers.ModelSerializer):
    skills = serializers.StringRelatedField(many=True, read_only=True)
    avatar_url = serializers.SerializerMethodField()
    project_count = serializers.IntegerField(read_only=True)
    asset_count = serializers.IntegerField(read_only=True)
    level_progress = serializers.IntegerField(read_only=True)
    follower_count = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["id","username","email","full_name","role","bio","location","website",
                  "github","level","xp","level_progress","subscription_type","is_verified",
                  "avatar_url","project_count","asset_count","skills","follower_count","created_at"]
    def get_avatar_url(self, obj):
        r = self.context.get("request")
        return r.build_absolute_uri(obj.avatar.url) if obj.avatar and r else None
    def get_follower_count(self, obj):
        return obj.followers.count()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["full_name", "bio", "location", "website", "github", "role"]
        extra_kwargs = {f: {"required": False} for f in ["full_name","bio","location","website","github","role"]}


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ["username", "email", "full_name", "password", "password2"]
        extra_kwargs = {"email": {"required": True}, "full_name": {"required": False}}
    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password": "Parollar mos kelmadi."})
        return attrs
    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=validated_data.get("full_name", ""),
        )


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)
    def validate(self, attrs):
        login = attrs.get("login")
        password = attrs.get("password")
        user = None
        if "@" in login:
            try:
                u = User.objects.get(email__iexact=login)
                user = authenticate(username=u.username, password=password)
            except User.DoesNotExist:
                pass
        else:
            user = authenticate(username=login, password=password)
        if not user:
            raise serializers.ValidationError("Login yoki parol noto'g'ri.")
        if not user.is_active:
            raise serializers.ValidationError("Hisob faol emas.")
        attrs["user"] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Eski parol noto'g'ri.")
        return value


class ProjectSerializer(serializers.ModelSerializer):
    creator = UserMinSerializer(read_only=True)
    tech_stack = TagSerializer(many=True, read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = ["id","title","description","genre","status","visibility",
                  "creator","tech_stack","member_count","thumbnail_url","max_members","created_at"]
    def get_thumbnail_url(self, obj):
        r = self.context.get("request")
        return r.build_absolute_uri(obj.thumbnail.url) if obj.thumbnail and r else None


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserMinSerializer(read_only=True)
    class Meta:
        model = Task
        fields = ["id","title","description","status","priority","due_date","assigned_to","created_at"]


class PostSerializer(serializers.ModelSerializer):
    author = UserMinSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ["id","author","post_type","content","code","code_lang",
                  "tags","is_public","like_count","comment_count","is_liked","created_at"]
    def get_like_count(self, obj): return obj.likes.count()
    def get_comment_count(self, obj): return obj.comments.count()
    def get_is_liked(self, obj):
        r = self.context.get("request")
        return obj.likes.filter(user=r.user).exists() if r and r.user.is_authenticated else False


class CommentSerializer(serializers.ModelSerializer):
    author = UserMinSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ["id","author","content","parent","created_at"]


class JobSerializer(serializers.ModelSerializer):
    client = UserMinSerializer(read_only=True)
    skills_needed = TagSerializer(many=True, read_only=True)
    proposal_count = serializers.SerializerMethodField()
    class Meta:
        model = Job
        fields = ["id","title","description","budget","visibility","status",
                  "deadline","client","skills_needed","proposal_count","created_at"]
    def get_proposal_count(self, obj): return obj.proposals.count()


class ProposalSerializer(serializers.ModelSerializer):
    worker = UserMinSerializer(read_only=True)
    class Meta:
        model = Proposal
        fields = ["id","job","worker","price","message","delivery_days","status","created_at"]
        read_only_fields = ["worker","status"]


class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = ["id","name","slug","icon"]


class AssetSerializer(serializers.ModelSerializer):
    creator = UserMinSerializer(read_only=True)
    category = AssetCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=AssetCategory.objects.all(), source="category",
        write_only=True, required=False, allow_null=True)
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    class Meta:
        model = Asset
        fields = ["id","title","description","format","price","tags","downloads",
                  "like_count","is_liked","is_approved","creator","category","category_id",
                  "file_url","thumbnail_url","created_at"]
        read_only_fields = ["downloads","is_approved","creator"]
    def get_file_url(self, obj):
        r = self.context.get("request")
        return r.build_absolute_uri(obj.file.url) if obj.file and r else None
    def get_thumbnail_url(self, obj):
        r = self.context.get("request")
        return r.build_absolute_uri(obj.thumbnail.url) if obj.thumbnail and r else None
    def get_like_count(self, obj): return obj.likes.count()
    def get_is_liked(self, obj):
        r = self.context.get("request")
        return obj.likes.filter(pk=r.user.pk).exists() if r and r.user.is_authenticated else False


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserMinSerializer(read_only=True)
    icon = serializers.CharField(read_only=True)
    class Meta:
        model = Notification
        fields = ["id","sender","notif_type","title","message","link","is_read","icon","created_at"]
        read_only_fields = ["sender","notif_type","title","message","link","icon"]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserMinSerializer(read_only=True)
    attachment_url = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = ["id","sender","content","attachment_url","is_read","created_at"]
        read_only_fields = ["sender","is_read"]
    def get_attachment_url(self, obj):
        r = self.context.get("request")
        return r.build_absolute_uri(obj.attachment.url) if obj.attachment and r else None


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserMinSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    class Meta:
        model = Conversation
        fields = ["id","participants","last_message","unread_count","created_at","updated_at"]
    def get_last_message(self, obj):
        msg = obj.last_message()
        if msg:
            return {"id": msg.id, "content": msg.content[:100] if msg.content else "",
                    "sender_username": msg.sender.username, "created_at": msg.created_at}
        return None
    def get_unread_count(self, obj):
        r = self.context.get("request")
        return obj.unread_count(r.user) if r and r.user.is_authenticated else 0
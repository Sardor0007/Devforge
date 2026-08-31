"""
DevForge REST API - ViewSets v2
JWT auth, Assets, Notifications, Messaging
"""
from rest_framework import viewsets, permissions, filters, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken

from django.db.models import Q, Count
from django.shortcuts import get_object_or_404

from apps.accounts.models import User
from apps.projects.models import Project, Task
from apps.feed.models import Post, Comment
from apps.jobs.models import Job, Proposal
from apps.tags.models import Tag
from apps.assets.models import Asset, AssetCategory
from apps.notifications.models import Notification
from apps.messaging.models import Conversation, Message

from .serializers import (
    UserMinSerializer, UserDetailSerializer, UserProfileUpdateSerializer,
    RegisterSerializer, LoginSerializer, ChangePasswordSerializer,
    ProjectSerializer, TaskSerializer,
    PostSerializer, CommentSerializer,
    JobSerializer, ProposalSerializer,
    TagSerializer, AssetSerializer, AssetCategorySerializer,
    NotificationSerializer, MessageSerializer, ConversationSerializer,
)


def get_tokens_for_user(user):
    """User uchun JWT access + refresh tokenlarini qaytaradi"""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access":  str(refresh.access_token),
    }


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


# ── AUTH VIEWS ────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """POST /api/v1/auth/register/"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response({
                "message": "Ro'yxatdan o'tish muvaffaqiyatli!",
                "user": UserMinSerializer(user, context={"request": request}).data,
                **tokens,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """POST /api/v1/auth/login/  — email/username + password -> JWT"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            tokens = get_tokens_for_user(user)
            return Response({
                "message": "Muvaffaqiyatli kirildi!",
                "user": UserDetailSerializer(user, context={"request": request}).data,
                **tokens,
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """POST /api/v1/auth/password/change/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data["new_password"])
            request.user.save()
            return Response({"message": "Parol muvaffaqiyatli o'zgartirildi."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── TAG ───────────────────────────────────────────────────────────────────────

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "slug"]

    @action(detail=False, methods=["get"])
    def popular(self, request):
        tags = Tag.popular(limit=20)
        return Response(TagSerializer(tags, many=True).data)


# ── USER ──────────────────────────────────────────────────────────────────────

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True).order_by("-created_at")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["username", "first_name", "last_name"]

    def get_serializer_class(self):
        return UserDetailSerializer if self.action == "retrieve" else UserMinSerializer

    @action(detail=False, methods=["get", "patch"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """GET /api/v1/users/me/ — profil | PATCH — yangilash"""
        if request.method == "PATCH":
            serializer = UserProfileUpdateSerializer(
                request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(UserDetailSerializer(request.user, context={"request": request}).data)
            return Response(serializer.errors, status=400)
        return Response(UserDetailSerializer(request.user, context={"request": request}).data)

    @action(detail=True, methods=["get"])
    def projects(self, request, pk=None):
        user = self.get_object()
        qs = Project.objects.filter(creator=user, visibility="public")
        return Response(ProjectSerializer(qs, many=True, context={"request": request}).data)


# ── PROJECT ───────────────────────────────────────────────────────────────────

class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title"]

    def get_queryset(self):
        qs = Project.objects.filter(visibility="public").select_related("creator")
        if g := self.request.query_params.get("genre"):
            qs = qs.filter(genre=g)
        if s := self.request.query_params.get("status"):
            qs = qs.filter(status=s)
        return qs

    def get_serializer_class(self): return ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=["get"])
    def tasks(self, request, pk=None):
        project = self.get_object()
        tasks = Task.objects.filter(project=project)
        return Response(TaskSerializer(tasks, many=True).data)


# ── FEED / POST ───────────────────────────────────────────────────────────────

class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["content"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        qs = Post.objects.filter(is_public=True).select_related("author")
        if t := self.request.query_params.get("type"):
            qs = qs.filter(post_type=t)
        if tag := self.request.query_params.get("tag"):
            qs = qs.filter(tags__slug=tag)
        return qs

    def get_serializer_class(self): return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        from apps.feed.models import PostLike
        post = self.get_object()
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            return Response({"liked": False, "count": post.likes.count()})
        return Response({"liked": True, "count": post.likes.count()})

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == "POST":
            if not request.user.is_authenticated:
                return Response({"detail": "Login required"}, status=401)
            comment = Comment.objects.create(
                post=post, author=request.user,
                content=request.data.get("content", ""))
            return Response(CommentSerializer(comment).data, status=201)
        return Response(CommentSerializer(post.comments.filter(parent=None), many=True).data)


# ── JOB ───────────────────────────────────────────────────────────────────────

class JobViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "budget"]

    def get_queryset(self):
        qs = Job.objects.filter(visibility="public").select_related("client")
        if s := self.request.query_params.get("status", "open"):
            qs = qs.filter(status=s)
        return qs

    def get_serializer_class(self): return JobSerializer

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def propose(self, request, pk=None):
        job = self.get_object()
        if job.client == request.user:
            return Response({"detail": "O'z jobingizga taklif bera olmaysiz."}, status=400)
        if Proposal.objects.filter(job=job, worker=request.user).exists():
            return Response({"detail": "Allaqachon taklif bergansiz."}, status=400)
        proposal = Proposal.objects.create(
            job=job, worker=request.user,
            price=request.data.get("price", job.budget),
            message=request.data.get("message", ""),
            delivery_days=request.data.get("delivery_days", 7),
        )
        return Response(ProposalSerializer(proposal).data, status=201)


# ── ASSETS ────────────────────────────────────────────────────────────────────

class AssetViewSet(viewsets.ModelViewSet):
    """GET/POST /api/v1/assets/"""
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "tags"]
    ordering_fields = ["created_at", "downloads", "price"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = Asset.objects.filter(is_approved=True).select_related("creator", "category")
        if f := self.request.query_params.get("format"):
            qs = qs.filter(format=f)
        if cat := self.request.query_params.get("category"):
            qs = qs.filter(category__slug=cat)
        if self.request.query_params.get("free") == "1":
            qs = qs.filter(price=0)
        return qs

    def get_serializer_class(self): return AssetSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        asset = self.get_object()
        if request.user in asset.likes.all():
            asset.likes.remove(request.user)
            return Response({"liked": False, "count": asset.likes.count()})
        asset.likes.add(request.user)
        return Response({"liked": True, "count": asset.likes.count()})

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        asset = self.get_object()
        asset.downloads += 1
        asset.save(update_fields=["downloads"])
        r = request.build_absolute_uri(asset.file.url) if asset.file else None
        return Response({"download_url": r, "filename": asset.file.name.split("/")[-1] if asset.file else ""})


# ── NOTIFICATIONS ─────────────────────────────────────────────────────────────

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/v1/notifications/"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).select_related("sender")

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.mark_read()
        return Response({"status": "read"})

    @action(detail=False, methods=["post"])
    def read_all(self, request):
        Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True)
        return Response({"status": "all read"})

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False).count()
        return Response({"count": count})


# ── MESSAGING ─────────────────────────────────────────────────────────────────

class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/v1/messages/"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related("participants").order_by("-updated_at")

    @action(detail=False, methods=["post"])
    def start(self, request):
        """POST /api/v1/messages/start/ — yangi suhbat boshlash {user_id}"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id talab qilinadi."}, status=400)
        try:
            other_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Foydalanuvchi topilmadi."}, status=404)
        conv = Conversation.get_or_create_between(request.user, other_user)
        return Response(ConversationSerializer(conv, context={"request": request}).data)

    @action(detail=True, methods=["get", "post"])
    def messages(self, request, pk=None):
        """GET/POST /api/v1/messages/{id}/messages/"""
        conv = self.get_object()
        if request.method == "POST":
            content = request.data.get("content", "").strip()
            if not content:
                return Response({"detail": "Xabar bo'sh bo'lishi mumkin emas."}, status=400)
            msg = Message.objects.create(
                conversation=conv,
                sender=request.user,
                content=content,
            )
            conv.updated_at = msg.created_at
            conv.save(update_fields=["updated_at"])
            return Response(MessageSerializer(msg, context={"request": request}).data, status=201)

        # Mark as read
        Message.objects.filter(
            conversation=conv, is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        msgs = conv.messages.select_related("sender").order_by("created_at")
        page = self.paginate_queryset(msgs)
        if page is not None:
            return self.get_paginated_response(
                MessageSerializer(page, many=True, context={"request": request}).data)
        return Response(MessageSerializer(msgs, many=True, context={"request": request}).data)
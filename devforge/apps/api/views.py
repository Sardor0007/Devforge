"""
DevForge REST API — ViewSets
"""
try:
    from rest_framework import viewsets, permissions, filters, status
    from rest_framework.decorators import action
    from rest_framework.response import Response
    from rest_framework.pagination import PageNumberPagination
except ImportError:
    raise ImportError("djangorestframework o'rnatilmagan.")

from django.db.models import Q
from apps.accounts.models import User
from apps.projects.models import Project, Task
from apps.feed.models import Post, Comment
from apps.jobs.models import Job, Proposal
from apps.tags.models import Tag
from .serializers import (
    UserMinSerializer, UserDetailSerializer,
    ProjectSerializer, TaskSerializer,
    PostSerializer, CommentSerializer,
    JobSerializer, ProposalSerializer,
    TagSerializer,
)


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ── TAG API ───────────────────────────────────────────────────────────────────

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/v1/tags/ — barcha teglar"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']

    @action(detail=False, methods=['get'])
    def popular(self, request):
        tags = Tag.popular(limit=20)
        return Response(TagSerializer(tags, many=True).data)


# ── USER API ──────────────────────────────────────────────────────────────────

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/v1/users/ — foydalanuvchilar"""
    queryset = User.objects.filter(is_active=True).order_by('-created_at')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserMinSerializer

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """GET /api/v1/users/me/ — o'z profilingiz"""
        return Response(UserDetailSerializer(request.user, context={'request': request}).data)

    @action(detail=True, methods=['get'])
    def projects(self, request, pk=None):
        """GET /api/v1/users/{id}/projects/ — foydalanuvchi loyihalari"""
        user = self.get_object()
        qs = Project.objects.filter(creator=user, visibility='public')
        return Response(ProjectSerializer(qs, many=True, context={'request': request}).data)


# ── PROJECT API ───────────────────────────────────────────────────────────────

class ProjectViewSet(viewsets.ModelViewSet):
    """CRUD /api/v1/projects/"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']

    def get_queryset(self):
        qs = Project.objects.filter(visibility='public').select_related('creator')
        genre = self.request.query_params.get('genre')
        status = self.request.query_params.get('status')
        if genre:
            qs = qs.filter(genre=genre)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_serializer_class(self):
        return ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        project = self.get_object()
        tasks = Task.objects.filter(project=project)
        return Response(TaskSerializer(tasks, many=True).data)


# ── FEED / POST API ───────────────────────────────────────────────────────────

class PostViewSet(viewsets.ModelViewSet):
    """CRUD /api/v1/posts/"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['content']
    ordering_fields = ['created_at']

    def get_queryset(self):
        qs = Post.objects.filter(is_public=True).select_related('author')
        post_type = self.request.query_params.get('type')
        tag = self.request.query_params.get('tag')
        if post_type:
            qs = qs.filter(post_type=post_type)
        if tag:
            qs = qs.filter(tags__slug=tag)
        return qs

    def get_serializer_class(self):
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """POST /api/v1/posts/{id}/like/"""
        post = self.get_object()
        from apps.feed.models import PostLike
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            return Response({'liked': False, 'count': post.likes.count()})
        return Response({'liked': True, 'count': post.likes.count()})

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """GET/POST /api/v1/posts/{id}/comments/"""
        post = self.get_object()
        if request.method == 'POST':
            if not request.user.is_authenticated:
                return Response({'detail': 'Login required'}, status=status.HTTP_401_UNAUTHORIZED)
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=request.data.get('content', '')
            )
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        comments = post.comments.filter(parent=None)
        return Response(CommentSerializer(comments, many=True).data)


# ── JOB API ───────────────────────────────────────────────────────────────────

class JobViewSet(viewsets.ModelViewSet):
    """CRUD /api/v1/jobs/"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'budget']

    def get_queryset(self):
        qs = Job.objects.filter(visibility='public').select_related('client')
        job_status = self.request.query_params.get('status', 'open')
        if job_status:
            qs = qs.filter(status=job_status)
        return qs

    def get_serializer_class(self):
        return JobSerializer

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def propose(self, request, pk=None):
        """POST /api/v1/jobs/{id}/propose/ — taklif yuborish"""
        job = self.get_object()
        if job.client == request.user:
            return Response({'detail': "O'z jobingizga taklif bera olmaysiz."}, status=400)
        if Proposal.objects.filter(job=job, worker=request.user).exists():
            return Response({'detail': "Allaqachon taklif bergansiz."}, status=400)

        proposal = Proposal.objects.create(
            job=job,
            worker=request.user,
            price=request.data.get('price', job.budget),
            message=request.data.get('message', ''),
            delivery_days=request.data.get('delivery_days', 7),
        )
        return Response(ProposalSerializer(proposal).data, status=status.HTTP_201_CREATED)

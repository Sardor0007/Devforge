from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from apps.accounts.models import User
from apps.notifications.service import notify
from .models import Post, PostLike, Comment, Follow


def feed_view(request):
    tab = request.GET.get('tab', 'all' if not request.user.is_authenticated else 'following')

    if tab == 'following' and request.user.is_authenticated:
        following_ids = request.user.following.values_list('following_id', flat=True)
        posts = Post.objects.filter(
            Q(author__in=following_ids) | Q(author=request.user),
            is_public=True
        ).select_related('author').prefetch_related('likes', 'comments')
    elif tab == 'trending':
        posts = Post.objects.filter(is_public=True).select_related('author').prefetch_related('likes', 'comments').annotate(
            like_cnt=Count('likes')
        ).order_by('-like_cnt', '-created_at')
    else:
        posts = Post.objects.filter(is_public=True).select_related('author').prefetch_related('likes', 'comments')

    # Tag filter
    tag = request.GET.get('tag', '').strip()
    if tag:
        posts = posts.filter(
            Q(tags__name__icontains=tag) | Q(tags__slug__icontains=tag) | Q(content__icontains=tag)
        ).distinct()

    posts = posts.order_by('-created_at')
    paginator = Paginator(posts, 15)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    # Suggested users & liked pks — only for authenticated users
    suggested  = []
    liked_pks  = set()
    if request.user.is_authenticated:
        following_ids = list(request.user.following.values_list('following_id', flat=True))
        suggested = User.objects.exclude(
            pk__in=following_ids + [request.user.pk]
        ).annotate(follower_count=Count('followers')).order_by('-follower_count')[:5]
        liked_pks = set(PostLike.objects.filter(user=request.user).values_list('post_id', flat=True))

    trending_tags = ['unity', 'blender', 'gamedev', 'shaders', 'unreal', '3d', 'godot', 'pixelart']

    return render(request, 'feed/feed.html', {
        'posts':         page_obj,
        'page_obj':      page_obj,
        'tab':           tab,
        'tag':           tag,
        'suggested':     suggested,
        'liked_pks':     liked_pks,
        'trending_tags': trending_tags,
    })


@login_required
def post_create_view(request):
    if request.method == 'POST':
        content   = request.POST.get('content', '').strip()
        post_type = request.POST.get('post_type', 'text')
        code      = request.POST.get('code', '')
        code_lang = request.POST.get('code_lang', 'python')
        tags      = request.POST.get('tags', '')
        image     = request.FILES.get('image')
        video     = request.FILES.get('video')

        if not content:
            messages.error(request, "Matn bo'sh bo'lishi mumkin emas.")
            return redirect('feed')

        # Parse tags
        tag_objects = []
        if tags:
            from apps.tags.models import Tag
            for tag_name in tags.split(','):
                tag_name = tag_name.strip()
                if tag_name:
                    tag_objects.append(Tag.get_or_create_tag(tag_name))

        post = Post.objects.create(
            author=request.user,
            content=content,
            post_type=post_type,
            code=code,
            code_lang=code_lang,
            image=image,
            video=video,
        )
        
        if tag_objects:
            post.tags.set(tag_objects)

        # Log Activity & Award XP
        try:
            from apps.accounts.models import UserActivity
            UserActivity.log_activity(request.user, 'post')
        except Exception as e:
            print(f"Failed to log post creation activity: {e}")

        # Bildirishnoma — following larga
        for follow in request.user.followers.all():
            notify(
                recipient=follow.follower,
                sender=request.user,
                notif_type='post_created',
                title=f"{request.user.username} yangi post qo'shdi",
                message=content[:80],
                link=f'/feed/post/{post.pk}/',
            )

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok', 'post_id': post.pk})
        messages.success(request, "Post qo'shildi!")
        return redirect('feed')

    return redirect('feed')


@login_required
def post_detail_view(request, pk):
    post     = get_object_or_404(Post, pk=pk)
    comments = post.comments.filter(parent=None).select_related('author').prefetch_related('replies__author')
    is_liked = PostLike.objects.filter(post=post, user=request.user).exists()
    return render(request, 'feed/post_detail.html', {
        'post':     post,
        'comments': comments,
        'is_liked': is_liked,
    })


@login_required
@require_POST
def post_like_view(request, pk):
    post  = get_object_or_404(Post, pk=pk)
    like, created = PostLike.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        if post.author != request.user:
            notify(
                recipient=post.author,
                sender=request.user,
                notif_type='post_liked',
                title=f"{request.user.username} postingizni yoqtirdi",
                message=post.content[:60],
                link=f'/feed/post/{post.pk}/',
            )

    return JsonResponse({'liked': liked, 'count': post.like_count()})


@login_required
@require_POST
def comment_add_view(request, pk):
    post    = get_object_or_404(Post, pk=pk)
    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')

    if not content:
        return JsonResponse({'error': 'Bo\'sh izoh'}, status=400)

    parent = Comment.objects.filter(pk=parent_id).first() if parent_id else None
    comment = Comment.objects.create(
        post=post, author=request.user, content=content, parent=parent
    )

    # Log Activity & Award XP
    try:
        from apps.accounts.models import UserActivity
        UserActivity.log_activity(request.user, 'comment')
    except Exception as e:
        print(f"Failed to log comment activity: {e}")

    if post.author != request.user:
        notify(
            recipient=post.author,
            sender=request.user,
            notif_type='comment_added',
            title=f"{request.user.username} postingizga izoh qoldirdi",
            message=content[:60],
            link=f'/feed/post/{post.pk}/',
        )

    return JsonResponse({
        'id':      comment.pk,
        'author':  comment.author.username,
        'content': comment.content,
        'time':    comment.created_at.strftime('%d %b, %H:%M'),
    })


@login_required
@require_POST
def post_delete_view(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.delete()
    return redirect('feed')


@login_required
@require_POST
def follow_toggle_view(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({'error': 'O\'zingizni kuzatolmaysiz'}, status=400)

    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        follow.delete()
        following = False
    else:
        following = True
        notify(
            recipient=target,
            sender=request.user,
            notif_type='new_follower',
            title=f"{request.user.username} sizni kuzata boshladi",
            message='',
            link=f'/auth/profile/{request.user.username}/',
        )

    followers_count = target.followers.count()
    return JsonResponse({'following': following, 'followers_count': followers_count})


@login_required
def user_feed_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile_user, is_public=True)
    paginator = Paginator(posts, 10)
    page_obj  = paginator.get_page(request.GET.get('page', 1))
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    return render(request, 'feed/user_feed.html', {
        'profile_user': profile_user,
        'posts':        page_obj,
        'page_obj':     page_obj,
        'is_following': is_following,
        'followers_count': profile_user.followers.count(),
        'following_count': profile_user.following.count(),
    })

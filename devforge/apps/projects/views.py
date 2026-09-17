from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, Http404, JsonResponse
import os, mimetypes
from .models import Project, ProjectRole, ProjectMember, Task, ProjectDownloadPermission
from .forms import ProjectForm, ProjectRoleForm, TaskForm


@login_required
def dashboard_view(request):
    from apps.accounts.views import dashboard_view as acc_dashboard
    return acc_dashboard(request)


@login_required
def project_list_view(request):
    query = request.GET.get('q', '')
    genre = request.GET.get('genre', '')
    status = request.GET.get('status', '')
    projects = Project.objects.filter(visibility='public').select_related('creator').prefetch_related('members', 'tasks')
    if query:
        projects = projects.filter(
            Q(title__icontains=query)|Q(description__icontains=query)|Q(tech_stack__icontains=query)
        )
    if genre:   projects = projects.filter(genre=genre)
    if status:  projects = projects.filter(status=status)
    from django.core.paginator import Paginator
    paginator = Paginator(projects.order_by('-created_at'), 9)
    page_obj  = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'projects/list.html', {
        'projects': page_obj, 'page_obj': page_obj,
        'query': query, 'genre': genre, 'status': status,
        'genre_choices': Project.GENRE_CHOICES, 'status_choices': Project.STATUS_CHOICES,
    })


@login_required
def project_create_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user
            project.save()
            
            # Log Activity & Award XP
            try:
                from apps.accounts.models import UserActivity
                UserActivity.log_activity(request.user, 'project')
            except Exception as e:
                print(f"Failed to log project creation activity: {e}")

            messages.success(request, f"'{project.title}' loyihasi yaratildi!")
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/create.html', {'form': form})





@login_required
def project_apply_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.creator == request.user:
        messages.error(request, "O'z loyihangizga ariza bera olmaysiz.")
        return redirect('project_detail', pk=pk)
    if project.members.filter(user=request.user).exists():
        messages.warning(request, "Siz allaqachon ariza bergansiz yoki a'zosiz.")
        return redirect('project_detail', pk=pk)
    if request.method == 'POST':
        message = request.POST.get('message', '')
        role_id = request.POST.get('role_id')
        role = None
        if role_id:
            role = ProjectRole.objects.filter(pk=role_id, project=project).first()
        ProjectMember.objects.create(
            project=project, user=request.user, role=role,
            message=message, is_approved=False
        )
        try:
            from apps.notifications.service import notify_project_apply
            notify_project_apply(project, request.user)
        except Exception:
            pass
        messages.success(request, "Arizangiz yuborildi! Loyiha egasi ko'rib chiqadi.")
    return redirect('project_detail', pk=pk)


@login_required
def project_approve_member_view(request, pk, member_pk):
    project = get_object_or_404(Project, pk=pk, creator=request.user)
    member = get_object_or_404(ProjectMember, pk=member_pk, project=project)
    member.is_approved = True
    member.save()
    try:
        from apps.notifications.service import notify_project_approved, notify_new_member
        notify_project_approved(member.user, project)
        notify_new_member(project, member.user)
    except Exception:
        pass
    messages.success(request, f"{member.user.username} loyihaga qabul qilindi!")
    return redirect('project_detail', pk=pk)


@login_required
def task_create_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    is_member = project.members.filter(user=request.user, is_approved=True).exists()
    if not (project.creator == request.user or is_member):
        messages.error(request, "Ruxsat yo'q.")
        return redirect('project_detail', pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            try:
                from apps.notifications.service import notify_task_assigned
                notify_task_assigned(task, request.user)
            except Exception:
                pass
            messages.success(request, "Vazifa qo'shildi!")
            return redirect('project_detail', pk=pk)
    else:
        form = TaskForm(project=project)
    return render(request, 'projects/task_form.html', {'form': form, 'project': project})


@login_required
def task_update_status_view(request, pk, task_pk):
    project = get_object_or_404(Project, pk=pk)
    task = get_object_or_404(Task, pk=task_pk, project=project)
    new_status = request.POST.get('status')
    if new_status in dict(Task.STATUS_CHOICES):
        old_status = task.status
        task.status = new_status
        task.save()
        if new_status == 'done' and old_status != 'done':
            # Log Activity & Award XP
            try:
                from apps.accounts.models import UserActivity
                target_user = task.assigned_to if task.assigned_to else request.user
                UserActivity.log_activity(target_user, 'task')
            except Exception as e:
                print(f"Failed to log task completion activity: {e}")

            try:
                from apps.notifications.service import notify_task_completed
                notify_task_completed(task, request.user)
            except Exception:
                pass
    return redirect('project_detail', pk=pk)


# ═══════════════════════════════════════════════════════════════
#  DOWNLOAD SYSTEM
# ═══════════════════════════════════════════════════════════════

def _has_download_access(project, user):
    """
    Yuklab olish ruxsatini tekshiradi.
    Returns: (allowed: bool, reason: str)
    """
    if not user.is_authenticated:
        return False, 'login_required'

    # Loyiha egasi har doim ruxsatga ega
    if project.creator == user:
        return True, 'owner'

    # Yuklab olish yoqilmagan bo'lsa
    if not project.download_enabled:
        return False, 'download_disabled'

    # Obuna tekshirish (pro, studio, enterprise, gold, platinum)
    if not user.can_use_pro_features():
        return False, 'subscription_required'

    # Egasi ruxsat berganligi tekshiruvi
    has_permission = project.download_permissions.filter(user=user).exists()
    if not has_permission:
        return False, 'permission_required'

    return True, 'granted'


@login_required
def project_detail_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    members = project.members.filter(is_approved=True).select_related('user', 'role')
    open_roles = project.roles.filter(is_filled=False)
    pending_requests = project.members.filter(is_approved=False).select_related('user')
    tasks = project.tasks.select_related('assigned_to').all()
    is_member = project.members.filter(user=request.user, is_approved=True).exists()
    is_creator = project.creator == request.user
    has_pending = project.members.filter(user=request.user, is_approved=False).exists()

    # Download context
    download_allowed, download_reason = _has_download_access(project, request.user)
    download_permissions_list = []
    if is_creator:
        download_permissions_list = project.download_permissions.select_related('user', 'granted_by').order_by('-granted_at')
        permitted_user_ids = set(download_permissions_list.values_list('user_id', flat=True))
        for member in members:
            member.has_download_perm = member.user_id in permitted_user_ids

    return render(request, 'projects/detail.html', {
        'project': project, 'members': members, 'open_roles': open_roles,
        'pending_requests': pending_requests, 'tasks': tasks,
        'is_member': is_member, 'is_creator': is_creator, 'has_pending': has_pending,
        # Download
        'download_allowed': download_allowed,
        'download_reason': download_reason,
        'download_permissions_list': download_permissions_list,
    })


@login_required
def project_upload_file_view(request, pk):
    """Loyiha egasi yuklab olinadigan faylni yuklaydi."""
    project = get_object_or_404(Project, pk=pk, creator=request.user)
    if request.method == 'POST':
        uploaded = request.FILES.get('project_file')
        if not uploaded:
            messages.error(request, "Fayl tanlanmadi.")
            return redirect('project_detail', pk=pk)

        # Fayl hajmi: max 500MB
        max_size = 500 * 1024 * 1024
        if uploaded.size > max_size:
            messages.error(request, "Fayl hajmi 500MB dan oshmasligi kerak.")
            return redirect('project_detail', pk=pk)

        # Eski faylni o'chirish
        if project.project_file:
            try:
                old_path = project.project_file.path
                if os.path.exists(old_path):
                    os.remove(old_path)
            except Exception:
                pass

        project.project_file = uploaded
        project.save(update_fields=['project_file'])
        messages.success(request, f"'{uploaded.name}' fayli muvaffaqiyatli yuklandi!")
    return redirect('project_detail', pk=pk)


@login_required
def project_toggle_download_view(request, pk):
    """Egasi yuklab olishni yoqadi / o'chiradi."""
    project = get_object_or_404(Project, pk=pk, creator=request.user)
    if request.method == 'POST':
        if not project.project_file:
            messages.error(request, "Avval loyiha faylini yuklang.")
            return redirect('project_detail', pk=pk)
        project.download_enabled = not project.download_enabled
        project.save(update_fields=['download_enabled'])
        state = "yoqildi ✅" if project.download_enabled else "o'chirildi ❌"
        messages.success(request, f"Yuklab olish {state}")
    return redirect('project_detail', pk=pk)


@login_required
def project_download_view(request, pk):
    """Foydalanuvchi loyiha faylini yuklab oladi."""
    project = get_object_or_404(Project, pk=pk)

    allowed, reason = _has_download_access(project, request.user)
    if not allowed:
        reason_map = {
            'download_disabled': "Bu loyiha uchun yuklab olish yoqilmagan.",
            'subscription_required': "Loyihani yuklab olish uchun Pro obuna kerak.",
            'permission_required': "Loyiha egasi sizga yuklab olish ruxsatini bermagan.",
        }
        messages.error(request, reason_map.get(reason, "Ruxsat yo'q."))
        return redirect('project_detail', pk=pk)

    if not project.project_file:
        messages.error(request, "Loyiha fayli hali yuklanmagan.")
        return redirect('project_detail', pk=pk)

    try:
        file_path = project.project_file.path
        if not os.path.exists(file_path):
            raise Http404("Fayl topilmadi.")

        file_name = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'

        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            response['Content-Length'] = os.path.getsize(file_path)
            return response
    except Http404:
        raise
    except Exception as e:
        messages.error(request, "Fayl yuklab olishda xatolik yuz berdi.")
        return redirect('project_detail', pk=pk)


@login_required
def project_grant_download_view(request, pk, user_pk=None):
    """Egasi biror foydalanuvchiga yuklab olish ruxsatini beradi."""
    project = get_object_or_404(Project, pk=pk, creator=request.user)
    from apps.accounts.models import User

    if request.method == 'POST':
        target_user = None
        if user_pk:
            target_user = get_object_or_404(User, pk=user_pk)
        else:
            uname = request.POST.get('username', '').strip()
            uid = request.POST.get('user_id')
            if uid:
                target_user = User.objects.filter(pk=uid).first()
            elif uname:
                target_user = User.objects.filter(username__iexact=uname).first()
            
            if not target_user:
                messages.error(request, f"Foydalanuvchi topilmadi: {uname or uid}")
                return redirect('project_detail', pk=pk)

        if target_user == request.user:
            messages.warning(request, "O'zingizga ruxsat berishingiz shart emas.")
            return redirect('project_detail', pk=pk)

        _, created = ProjectDownloadPermission.objects.get_or_create(
            project=project,
            user=target_user,
            defaults={'granted_by': request.user}
        )
        if created:
            messages.success(request, f"@{target_user.username} ga yuklab olish ruxsati berildi ✅")
        else:
            messages.info(request, f"@{target_user.username} allaqachon ruxsatga ega.")
    return redirect('project_detail', pk=pk)


@login_required
def project_revoke_download_view(request, pk, user_pk):
    """Egasi biror foydalanuvchining ruxsatini olib qo'yadi."""
    project = get_object_or_404(Project, pk=pk, creator=request.user)
    if request.method == 'POST':
        deleted, _ = ProjectDownloadPermission.objects.filter(
            project=project, user_id=user_pk
        ).delete()
        if deleted:
            messages.success(request, "Ruxsat olib qo'yildi.")
        else:
            messages.warning(request, "Bu foydalanuvchida ruxsat yo'q edi.")
    return redirect('project_detail', pk=pk)

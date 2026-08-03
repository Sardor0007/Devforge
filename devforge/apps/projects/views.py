from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Project, ProjectRole, ProjectMember, Task
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
def project_detail_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    members = project.members.filter(is_approved=True).select_related('user', 'role')
    open_roles = project.roles.filter(is_filled=False)
    pending_requests = project.members.filter(is_approved=False).select_related('user')
    tasks = project.tasks.select_related('assigned_to').all()
    is_member = project.members.filter(user=request.user, is_approved=True).exists()
    is_creator = project.creator == request.user
    has_pending = project.members.filter(user=request.user, is_approved=False).exists()
    return render(request, 'projects/detail.html', {
        'project': project, 'members': members, 'open_roles': open_roles,
        'pending_requests': pending_requests, 'tasks': tasks,
        'is_member': is_member, 'is_creator': is_creator, 'has_pending': has_pending,
    })


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

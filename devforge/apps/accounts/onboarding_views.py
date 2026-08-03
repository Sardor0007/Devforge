from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Skill

from django.http import JsonResponse
from django.views.decorators.http import require_POST

ONBOARDING_SKILLS = [
    'Unity', 'Unreal Engine', 'Godot', 'GameMaker',
    'Blender', 'Maya', 'ZBrush', '3ds Max',
    'C#', 'C++', 'Python', 'GDScript', 'Lua',
    'UI/UX', 'Shader Coding', 'Character Art',
    'Sound Design', 'Level Design', 'Game Design',
]

@login_required
def onboarding_view(request):
    if request.user.onboarding_completed:
        return redirect('dashboard')

    if request.method == 'POST':
        role = request.POST.get('role')
        skills = request.POST.getlist('skills')

        if role:
            request.user.role = role
            request.user.onboarding_completed = True
            request.user.save()

            for skill_name in skills:
                Skill.objects.get_or_create(user=request.user, name=skill_name)

            return redirect('dashboard')

    return render(request, 'accounts/onboarding.html', {
        'skills': ONBOARDING_SKILLS,
    })


@login_required
@require_POST
def complete_tour_api(request):
    """AJAX endpoint: Onboarding tour yakunlanganda bajariladi"""
    request.user.onboarding_completed = True
    request.user.save(update_fields=['onboarding_completed'])
    return JsonResponse({'status': 'ok'})

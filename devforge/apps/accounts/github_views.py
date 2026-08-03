"""
GitHub integratsiya — foydalanuvchi GitHub reposini DevForge'ga import qilish
"""
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
import json


GITHUB_API = "https://api.github.com"


def _get_github_headers(token=None):
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
    return headers


@login_required
def github_sync_repos(request):
    """
    GitHub profilidan repo'larni sinxronlash.
    Foydalanuvchi GitHub OAuth bilan kirgan bo'lishi kerak.
    """
    from allauth.socialaccount.models import SocialToken, SocialAccount
    from apps.accounts.models import SocialProfile

    # GitHub OAuth token olish
    try:
        social_account = SocialAccount.objects.get(user=request.user, provider='github')
        token_obj = SocialToken.objects.get(account=social_account)
        access_token = token_obj.token
    except (SocialAccount.DoesNotExist, SocialToken.DoesNotExist):
        messages.error(request, "GitHub akkauntingiz bog'lanmagan. Avval GitHub orqali kiring.")
        return redirect('profile', username=request.user.username)

    # GitHub username
    github_username = social_account.extra_data.get('login', '')

    try:
        # Foydalanuvchi repo'larini olish
        resp = requests.get(
            f"{GITHUB_API}/users/{github_username}/repos",
            headers=_get_github_headers(access_token),
            params={'sort': 'updated', 'per_page': 30, 'type': 'owner'},
            timeout=10
        )
        resp.raise_for_status()
        repos = resp.json()

        # Faqat kerakli maydonlarni saqlash
        clean_repos = []
        for r in repos:
            clean_repos.append({
                'id': r.get('id'),
                'name': r.get('name'),
                'full_name': r.get('full_name'),
                'description': r.get('description', '') or '',
                'url': r.get('html_url'),
                'stars': r.get('stargazers_count', 0),
                'forks': r.get('forks_count', 0),
                'language': r.get('language', ''),
                'updated_at': r.get('updated_at', ''),
                'is_private': r.get('private', False),
            })

        # SocialProfile'ga saqlash
        social_profile, _ = SocialProfile.objects.get_or_create(
            user=request.user,
            defaults={'provider': 'github', 'github_username': github_username}
        )
        social_profile.github_username = github_username
        social_profile.github_repos = clean_repos
        social_profile.repos_synced_at = timezone.now()
        social_profile.github_url = f"https://github.com/{github_username}"
        social_profile.save()

        messages.success(request, f"✅ {len(clean_repos)} ta GitHub repo sinxronlandi!")

    except requests.RequestException as e:
        messages.error(request, f"GitHub API xatosi: {str(e)}")

    return redirect('profile', username=request.user.username)


@login_required
def github_import_repo(request, repo_name):
    """
    Bitta GitHub repo'ni DevForge Projectiga import qilish
    """
    from allauth.socialaccount.models import SocialToken, SocialAccount
    from apps.projects.models import Project
    from apps.accounts.models import SocialProfile

    try:
        social_account = SocialAccount.objects.get(user=request.user, provider='github')
        token_obj = SocialToken.objects.get(account=social_account)
        access_token = token_obj.token
        github_username = social_account.extra_data.get('login', '')
    except (SocialAccount.DoesNotExist, SocialToken.DoesNotExist):
        messages.error(request, "GitHub akkauntingiz bog'lanmagan.")
        return redirect('project_list')

    try:
        resp = requests.get(
            f"{GITHUB_API}/repos/{github_username}/{repo_name}",
            headers=_get_github_headers(access_token),
            timeout=10
        )
        resp.raise_for_status()
        repo = resp.json()

        # README.md ni olish
        readme_resp = requests.get(
            f"{GITHUB_API}/repos/{github_username}/{repo_name}/readme",
            headers=_get_github_headers(access_token),
            timeout=10
        )
        readme_content = ''
        if readme_resp.status_code == 200:
            import base64
            readme_data = readme_resp.json()
            try:
                readme_content = base64.b64decode(readme_data.get('content', '')).decode('utf-8')[:2000]
            except Exception:
                pass

        # Language → Tag
        language = repo.get('language', '') or ''

        if request.method == 'POST':
            # Loyiha yaratish
            project = Project.objects.create(
                creator=request.user,
                title=repo.get('name', repo_name),
                description=readme_content or repo.get('description', '') or f"GitHub: {repo_name}",
                visibility='public' if not repo.get('private') else 'private',
                status='active',
            )

            # Language tag qo'shish
            if language:
                from apps.tags.models import Tag
                tag = Tag.get_or_create_tag(language)
                project.tech_stack.add(tag)

            messages.success(request, f"✅ '{project.title}' loyihasi GitHub'dan import qilindi!")
            return redirect('project_detail', pk=project.pk)

        return render(request, 'github/import_repo.html', {
            'repo': repo,
            'repo_name': repo_name,
            'readme_content': readme_content,
            'language': language,
        })

    except requests.RequestException as e:
        messages.error(request, f"Repo import xatosi: {str(e)}")
        return redirect('project_list')


@login_required
def github_repos_api(request):
    """AJAX — foydalanuvchining saqlangan repo'larini qaytaradi"""
    from apps.accounts.models import SocialProfile
    try:
        profile = SocialProfile.objects.get(user=request.user)
        return JsonResponse({
            'repos': profile.github_repos,
            'synced_at': profile.repos_synced_at.isoformat() if profile.repos_synced_at else None,
            'github_url': profile.github_url,
        })
    except SocialProfile.DoesNotExist:
        return JsonResponse({'repos': [], 'synced_at': None})

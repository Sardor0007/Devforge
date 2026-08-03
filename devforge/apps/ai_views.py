"""
AI Feature views — Anthropic API orqali
- AI Task Generator (Projects → Kanban)
- AI Description Generator (Marketplace → Service)
- AI Job Description Generator (Jobs)
"""
import os
import json
import requests
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit


ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
ANTHROPIC_URL     = 'https://api.anthropic.com/v1/messages'
MODEL             = 'claude-sonnet-4-20250514'


def call_claude(system_prompt, user_prompt, max_tokens=1000):
    """Anthropic API ga so'rov yuborish"""
    if not ANTHROPIC_API_KEY:
        return None, "AI_KEY_MISSING"

    try:
        resp = requests.post(
            ANTHROPIC_URL,
            headers={
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            json={
                'model': MODEL,
                'max_tokens': max_tokens,
                'system': system_prompt,
                'messages': [{'role': 'user', 'content': user_prompt}],
            },
            timeout=30,
        )
        data = resp.json()
        if resp.status_code == 200:
            return data['content'][0]['text'], None
        return None, data.get('error', {}).get('message', 'API xatosi')
    except Exception as e:
        return None, str(e)


# ── AI TASK GENERATOR ─────────────────────────────────────────────────────────

@login_required
@require_POST
@ratelimit(key='user', rate='20/d', block=False)
def ai_generate_tasks(request):
    if getattr(request, 'limited', False):
        return JsonResponse({'error': "Siz kunlik so'rovlar limitiga yetdingiz. Iltimos, ertaga qayta urinib ko'ring."}, status=429)

    if not request.user.can_use_pro_features():
        return JsonResponse({
            'error': 'Bu funksiya faqat Gold va Platinum obunachilari uchun.',
            'upgrade_required': True
        }, status=403)

    data  = json.loads(request.body)
    title = data.get('project_title', '')
    desc  = data.get('project_description', '')
    genre = data.get('genre', '')
    count = min(int(data.get('count', 10)), 20)

    if not title or not desc:
        return JsonResponse({'error': 'Loyiha nomi va tavsifi kerak'}, status=400)

    system = """Siz o'yin ishlab chiqish loyihalari uchun vazifalar (task) generatoriIsiz.
Foydalanuvchi loyiha ma'lumotini beradi, siz aniq, amaliy vazifalar ro'yxatini yaratasiz.
FAQAT JSON qaytaring, boshqa hech narsa yo'q.
Format:
{"tasks": [{"title": "...", "description": "...", "priority": "high|medium|low", "category": "dev|art|design|audio|management"}]}"""

    prompt = f"""Loyiha: {title}
Janr: {genre}
Tavsif: {desc}

Shu loyiha uchun {count} ta aniq, bajarilishi mumkin bo'lgan vazifa yarat.
Vazifalar real o'yin ishlab chiqish jarayonini aks ettirsin (programmlash, 3D modeling, sound, QA va h.k.)"""

    result, error = call_claude(system, prompt, max_tokens=1500)

    if error:
        if error == "AI_KEY_MISSING":
            # Demo rejim — namuna vazifalar qaytarish
            demo_tasks = [
                {"title": "O'yin arxitekturasini loyihalash", "description": "Game Manager, Scene Manager, Event System yaratish", "priority": "high", "category": "dev"},
                {"title": "Asosiy karakter modeli", "description": "Low-poly karakter modeli va UV mapping", "priority": "high", "category": "art"},
                {"title": "Harakatlanish mexanikasi", "description": "Yurish, yugurish, sakrash animatsiyalari", "priority": "high", "category": "dev"},
                {"title": "UI/UX dizayn", "description": "Asosiy menyu, HUD, inventory dizayni", "priority": "medium", "category": "design"},
                {"title": "Audio sozlamalari", "description": "Fon musiqasi va sound effect integratsiyasi", "priority": "medium", "category": "audio"},
                {"title": "Birinchi level dizayni", "description": "Tutorial level layout va gameplay", "priority": "medium", "category": "dev"},
                {"title": "Dushman AI", "description": "Patrol, attack, damage state mashinalari", "priority": "medium", "category": "dev"},
                {"title": "Optimallashtirish", "description": "FPS optimizatsiyasi va profiling", "priority": "low", "category": "dev"},
                {"title": "Testlash", "description": "Bug report va QA jarayoni", "priority": "low", "category": "management"},
                {"title": "Build va chiqarish", "description": "Platform uchun build sozlamalari", "priority": "low", "category": "management"},
            ]
            return JsonResponse({'tasks': demo_tasks[:count], 'demo': True})
        return JsonResponse({'error': error}, status=500)

    try:
        # JSON ni tozalash
        text = result.strip()
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        parsed = json.loads(text)
        return JsonResponse(parsed)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'AI javobini tahlil qilib bo\'lmadi'}, status=500)


# ── AI DESCRIPTION GENERATOR ──────────────────────────────────────────────────

@login_required
@require_POST
@ratelimit(key='user', rate='20/d', block=False)
def ai_generate_description(request):
    if getattr(request, 'limited', False):
        return JsonResponse({'error': "Siz kunlik so'rovlar limitiga yetdingiz. Iltimos, ertaga qayta urinib ko'ring."}, status=429)

    if not request.user.can_use_pro_features():
        return JsonResponse({
            'error': 'Bu funksiya faqat Gold va Platinum obunachilari uchun.',
            'upgrade_required': True
        }, status=403)

    data     = json.loads(request.body)
    title    = data.get('title', '')
    category = data.get('category', '')
    keywords = data.get('keywords', '')
    tone     = data.get('tone', 'professional')

    if not title:
        return JsonResponse({'error': 'Xizmat nomi kerak'}, status=400)

    system = """Siz freelance marketplace uchun professional tavsif yozuvchisisiz.
O'yin sanoati (game development) kontekstida xizmatlar uchun jozibali, aniq tavsif yaratasiz.
FAQAT JSON qaytaring: {"description": "...", "short_desc": "...", "tags": ["...", "..."]}"""

    prompt = f"""Xizmat: {title}
Kategoriya: {category}
Kalit so'zlar: {keywords}
Uslub: {tone}

Bu xizmat uchun:
1. To'liq professional tavsif (150-200 so'z)
2. Qisqa tavsif (1-2 jumla)
3. 5-7 ta teglar yaratinghis"""

    result, error = call_claude(system, prompt, max_tokens=800)

    if error:
        if error == "AI_KEY_MISSING":
            return JsonResponse({
                'description': f"{title} — professional darajadagi {category} xizmati. Sifatli natija va o'z vaqtida yetkazib berish kafolatlanadi. Keng tajriba va portfolio asosida ishlaymiz.",
                'short_desc': f"Professional {title} xizmati. Sifat va muddatga kafolat.",
                'tags': [category, 'gamedev', 'professional', 'quality'],
                'demo': True,
            })
        return JsonResponse({'error': error}, status=500)

    try:
        text = result.strip()
        if '```json' in text: text = text.split('```json')[1].split('```')[0]
        elif '```' in text: text = text.split('```')[1].split('```')[0]
        return JsonResponse(json.loads(text))
    except:
        return JsonResponse({'error': 'Tahlil qilib bo\'lmadi'}, status=500)


# ── AI JOB DESCRIPTION ────────────────────────────────────────────────────────

@login_required
@require_POST
@ratelimit(key='user', rate='20/d', block=False)
def ai_generate_job_desc(request):
    if getattr(request, 'limited', False):
        return JsonResponse({'error': "Siz kunlik so'rovlar limitiga yetdingiz. Iltimos, ertaga qayta urinib ko'ring."}, status=429)

    if not request.user.can_use_pro_features():
        return JsonResponse({
            'error': 'Bu funksiya faqat Gold va Platinum obunachilari uchun.',
            'upgrade_required': True
        }, status=403)

    data  = json.loads(request.body)
    role  = data.get('role', '')
    project_type = data.get('project_type', '')
    skills = data.get('skills', '')

    system = """O'yin sanoati uchun ish e'lonlari yozuvchisisiz.
FAQAT JSON: {"description": "...", "requirements": "...", "skills": "..."}"""

    prompt = f"""Rol: {role}
Loyiha turi: {project_type}
Ko'nikmalar: {skills}

Bu rol uchun:
1. Jozibali tavsif (100-150 so'z)
2. Talablar ro'yxati (5-7 ta band)
3. Kerakli ko'nikmalar (vergul bilan)"""

    result, error = call_claude(system, prompt, max_tokens=600)

    if error == "AI_KEY_MISSING":
        return JsonResponse({
            'description': f"Bizning jamoaga {role} kerak! Loyihamizda ishtirok eting.",
            'requirements': "- Tegishli tajriba\n- Portfolio\n- Muloqotga tayyor",
            'skills': skills or 'Unity, C#, Git',
            'demo': True,
        })
    if error:
        return JsonResponse({'error': error}, status=500)

    try:
        text = result.strip()
        if '```json' in text: text = text.split('```json')[1].split('```')[0]
        elif '```' in text: text = text.split('```')[1].split('```')[0]
        return JsonResponse(json.loads(text))
    except:
        return JsonResponse({'error': 'Tahlil xatosi'}, status=500)


# ── AI SNIPPET EXPLAINER ──────────────────────────────────────────────────────

@login_required
@require_POST
@ratelimit(key='user', rate='50/d', block=False)
def ai_explain_code(request):
    if getattr(request, 'limited', False):
        return JsonResponse({'error': "Siz kunlik so'rovlar limitiga yetdingiz. Iltimos, ertaga qayta urinib ko'ring."}, status=429)

    if not request.user.can_use_pro_features():
        return JsonResponse({
            'error': 'Bu funksiya faqat Gold va Platinum obunachilari uchun.',
            'upgrade_required': True
        }, status=403)
    data = json.loads(request.body)
    code = data.get('code', '')
    lang = data.get('lang', 'python')

    if not code or len(code) > 3000:
        return JsonResponse({'error': 'Kod kiritilmagan yoki juda uzun'}, status=400)

    system = "Kod tahlilchisisiz. Qisqa, tushunarli tushuntirma bering. FAQAT JSON: {\"explanation\": \"...\", \"summary\": \"...\"}"
    prompt = f"Til: {lang}\n\nKod:\n{code}\n\nBu kodni tushuntirib bering."

    result, error = call_claude(system, prompt, max_tokens=500)

    if error == "AI_KEY_MISSING":
        return JsonResponse({'explanation': 'AI kaliti sozlanmagan. .env da ANTHROPIC_API_KEY ni kiriting.', 'demo': True})
    if error:
        return JsonResponse({'error': error}, status=500)

    try:
        text = result.strip()
        if '```json' in text: text = text.split('```json')[1].split('```')[0]
        elif '```' in text: text = text.split('```')[1].split('```')[0]
        return JsonResponse(json.loads(text))
    except:
        return JsonResponse({'explanation': result, 'summary': ''})

# ── AI FORMAT & REFACTOR CODE ──────────────────────────────────────────────────

@login_required
@require_POST
@ratelimit(key='user', rate='50/d', block=False)
def ai_format_code(request):
    if getattr(request, 'limited', False):
        return JsonResponse({'error': "Siz kunlik so'rovlar limitiga yetdingiz. Iltimos, ertaga qayta urinib ko'ring."}, status=429)

    if not request.user.can_use_pro_features():
        return JsonResponse({
            'error': 'Bu funksiya faqat Gold va Platinum obunachilari uchun.',
            'upgrade_required': True
        }, status=403)
    data = json.loads(request.body)
    code = data.get('code', '')
    lang = data.get('lang', 'python')

    if not code or len(code) > 5000:
        return JsonResponse({'error': 'Kod kiritilmagan yoki juda uzun'}, status=400)

    system = "Siz tajribali dasturchisiz. Berilgan kodni to'g'ri formatlang (Prettier/Black kabi), xatolarni to'g'rilang va qisqa sharh qoldiring. FAQAT JSON: {\"formatted_code\": \"...\", \"comments\": \"...\"}"
    prompt = f"Til: {lang}\n\nKod:\n{code}\n\nBu kodni chiroyli va to'g'ri formatlab bering. Kodning o'zini `formatted_code` da qaytaring."

    result, error = call_claude(system, prompt, max_tokens=2000)

    if error == "AI_KEY_MISSING":
        return JsonResponse({'formatted_code': code, 'comments': 'AI kaliti sozlanmagan. Demo rejimda o\'zgarishsiz qoldirildi.', 'demo': True})
    if error:
        return JsonResponse({'error': error}, status=500)

    try:
        text = result.strip()
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        return JsonResponse(json.loads(text))
    except Exception:
        return JsonResponse({'formatted_code': code, 'comments': 'JSONni tahlil qilib bo\'lmadi.'})

# ── AI DEBUG CODE ─────────────────────────────────────────────────────────────
@login_required
@require_POST
@ratelimit(key='user', rate='50/d', block=False)
def ai_debug_code(request):
    if getattr(request, 'limited', False):
        return JsonResponse({'error': "Siz kunlik so'rovlar limitiga yetdingiz. Iltimos, ertaga qayta urinib ko'ring."}, status=429)

    if not request.user.can_use_pro_features():
        return JsonResponse({
            'error': 'Bu funksiya faqat Gold va Platinum obunachilari uchun.',
            'upgrade_required': True
        }, status=403)
    data = json.loads(request.body)
    code = data.get('code', '')
    lang = data.get('lang', 'python')
    error_msg = data.get('error', 'Noma\'lum xato')

    if not code:
        return JsonResponse({'error': 'Kod kiritilmagan'}, status=400)

    system = "Siz tajribali debugging mutaxassisiz. Kod va xatolik matnini tahlil qiling. Tuzatilgan kodni va nima uchun xato bo'lganini tushuntiring. FAQAT JSON: {\"fixed_code\": \"...\", \"explanation\": \"...\"}"
    prompt = f"Til: {lang}\nXatolik: {error_msg}\n\nKod:\n{code}\n\nBu kodni tahlil qilib, tuzatilgan variantni bering."

    result, error = call_claude(system, prompt, max_tokens=2000)

    if error == "AI_KEY_MISSING":
        return JsonResponse({'fixed_code': code, 'explanation': 'AI kaliti sozlanmagan. Demo rejim.', 'demo': True})
    
    if error:
        return JsonResponse({'error': error}, status=500)

    try:
        text = result.strip()
        if '```json' in text: text = text.split('```json')[1].split('```')[0]
        elif '```' in text: text = text.split('```')[1].split('```')[0]
        return JsonResponse(json.loads(text))
    except:
        return JsonResponse({'fixed_code': code, 'explanation': result})

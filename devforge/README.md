# 🎮 DevForge — O'yin Ishlab Chiquvchilar Platformasi

## 🚀 Ishga Tushirish

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env faylini tahrirlang (quyida ko'rsatilgan)

python manage.py makemigrations accounts projects assets marketplace workspace notifications messaging feed jobs
python manage.py migrate
python manage.py createsuperuser

# Google/GitHub sozlash (quyida ko'rsatilgan)
python manage.py runserver
```
→ http://127.0.0.1:8000/

---

## 🔑 Google OAuth Sozlash

1. **https://console.cloud.google.com/** → kirish
2. Yangi loyiha yarating yoki mavjudini tanlang
3. **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
4. Application type: **Web application**
5. Authorized redirect URIs ga qo'shing:
   ```
   http://localhost:8000/accounts/google/callback/
   https://yourdomain.com/accounts/google/callback/
   ```
6. Client ID va Secret ni `.env` ga kiriting:
   ```
   GOOGLE_CLIENT_ID=....apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-...
   ```
7. **Django Admin** → Sites → `example.com` → `localhost:8000` ga o'zgartiring
8. **Django Admin** → Social Applications → Add:
   - Provider: Google
   - Client ID va Secret ID
   - Sites: localhost:8000

---

## 🐙 GitHub OAuth Sozlash

1. **https://github.com/settings/developers** → **New OAuth App**
2. To'ldiring:
   - Application name: `DevForge`
   - Homepage URL: `http://localhost:8000`
   - Callback URL: `http://localhost:8000/accounts/github/callback/`
3. Client ID va Secret ni `.env` ga kiriting:
   ```
   GITHUB_CLIENT_ID=Ov23li...
   GITHUB_CLIENT_SECRET=...
   ```
4. **Django Admin** → Social Applications → Add:
   - Provider: GitHub
   - Client ID va Secret
   - Sites: localhost:8000

---

## 📦 Barcha URL lar

| URL | Tavsif |
|---|---|
| `/` | Bosh sahifa |
| `/auth/login/` | Kirish (Email + Google + GitHub) |
| `/auth/register/` | Ro'yxatdan o'tish |
| `/auth/password-reset/` | Parol tiklash |
| `/accounts/google/login/` | Google OAuth |
| `/accounts/github/login/` | GitHub OAuth |
| `/dashboard/` | Shaxsiy boshqaruv |
| `/dashboard/projects/` | Loyihalar (Kanban + AI) |
| `/assets/` | 3D Aktivlar |
| `/marketplace/` | Freelance marketplace |
| `/workspace/<pk>/` | Kod muharriri + Terminal + Chat |
| `/feed/` | Ijtimoiy feed |
| `/jobs/` | Ish o'rinlari |
| `/messages/` | DM xabarlar |
| `/notifications/` | Bildirishnomalar |
| `/search/` | Global qidiruv |
| `/analytics/` | Admin panel |

---

## ⚙️ Production Deploy (Render)

```bash
# .env da:
DEBUG=False
SECRET_KEY=very-long-random-key
ALLOWED_HOSTS=yourapp.onrender.com
DATABASE_URL=postgresql://...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
ANTHROPIC_API_KEY=sk-ant-...

# Render callback URLlarini yangilang:
# https://yourapp.onrender.com/accounts/google/callback/
# https://yourapp.onrender.com/accounts/github/callback/
```

## 🛠 Stack
Django 5.0 · django-allauth · SQLite/PostgreSQL · Vanilla CSS · Gunicorn · Claude AI

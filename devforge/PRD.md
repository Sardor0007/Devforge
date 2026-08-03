# 🚀 DevForge — Mahsulot Talablari Hujjati (PRD)

## 1. Loyiha haqida

**DevForge** — o'yin ishlab chiqaruvchilar, 3D modelerlar, dasturchilar va ijodkorlar uchun maxsus platforma. Foydalanuvchilar loyiha yaratib, jamoa to'plashadi, fayllar ustida hamkorlik qilishadi va vazifalarni boshqarishadi.

---

## 2. Asosiy modullar

### 2.1 Autentifikatsiya (apps.accounts)
- Email + username bilan ro'yxatdan o'tish
- Google OAuth va GitHub OAuth orqali kirish
- Foydalanuvchi profili (avatar, rol, bio)
- Kuzatish / Kuzatuvchilar tizimi

### 2.2 Feed (apps.feed)
- Text, kod snippet, rasm postlar
- Tag tizimi (`#unity`, `#python`, ...)
- Like, izoh, ulashish
- Trending / Following / Hammasi taburlar
- Tavsiya etilgan foydalanuvchilar sidebar

### 2.3 Loyihalar (apps.projects)
- Loyiha yaratish (janr, holat, texnologiya stack)
- Jamoaga ariz berish va tasdiqlash
- Kanban vazifa boshqaruvi (Todo → InProgress → Done)
- 🤖 AI Vazifa Generatori (Anthropic Claude)
- Ochiq rollar (3D artist, developer, ...)

### 2.4 Workspace (apps.workspace)
- Har bir loyiha uchun virtual IDE
- **Fayl daraxti** — yaratish, o'chirish, qayta nomlash, papkalar
- **Kod muharriri** — sintaksis ranglar, qator raqamlari, tab tugmasi
- **Terminal** — shell buyruqlar, fayl sinxronlash (`_sync_workspace_to_disk`), **sandbox xavfsizligi**, yo'llarni virtualizatsiya qilish (real yo'llarni `~` bilan yashirish)
- **Chat** — real-time loyiha a'zolari bilan muloqot
- **Video Qo'ng'iroq** — Jitsi Meet integratsiyasi, real-time video va ovozli muloqot
- **Paket Menejeri** — `pip install --target` orqali loyihaga lokal kutubxonalar o'rnatish
- **GitHub integratsiya** — repolarni ko'rish va import qilish
- **"▶ Ishga tushirish"** tugmasi — `.py`, `.js`, `.sh` fayllarni ijro etish
- Fayl yuklash (drag & drop, papka yuklash)

### 2.5 Ish O'rinlari (apps.jobs)
- Vakansiya e'lon qilish (rol turi, ish turi, maosh)
- Ko'nikmalar bo'yicha filtrlash
- Arizalar tizimi
- Remote / On-site belgisi

### 2.6 3D Aktivlar (apps.assets)
- Model, tekstura, asset yuklash
- Kategoriya va format bo'yicha filtrlash
- Narx (bepul / pullik)
- **Savat (Cart)**: Pullik aktivlarni savatga qo'shish va sotib olish tizimi
- Yuklab olishlar va like'lar hisobi

### 2.7 Marketplace (apps.marketplace)
- Xizmat sotish / sotib olish
- Loyiha buyurtma berish

### 2.8 AI Integratsiya
- **Kod tushuntirish** (`/ai/explain-code/`) — fayl kodini Claude bilan tushuntirish
- **Vazifa generatsiyasi** (`/ai/generate-tasks/`) — loyiha uchun avtomatik vazifalar

### 2.9 3D Studio (apps.studio)
- Professional darajadagi 3D tahrirlash muhiti (Three.js)
- **Transform Controls** — siljitish, aylantirish, o'lchamni o'zgartirish
- **Material Tizimi** — PBR materiallar, tekstura yuklash, shaffoflik
- **Muhit** — HDR skyboxlar, tuman (fog), realistik yoritish
- **Eksport** — Sahnalarni GLTF formatida yuklab olish
- **Hierarchy** — Jism iyerarxiyasi va boshqaruvi

### 2.10 Boshqa modullar
- Bildirishnomalar (apps.notifications)
- **Xabarlar (apps.messaging)**: Matn, rasm, video va fayl yuborish. O'qilganlik (read receipt) tizimi.
- Analitika (apps.analytics)

---

## 3. Texnik stack

| Komponent | Texnologiya |
|-----------|-------------|
| Backend | Django 5.0 |
| Auth | django-allauth (email, Google, GitHub) |
| DB | SQLite (dev), PostgreSQL (prod) |
| Fayl saqlash | Django media (Pillow) |
| AI | Anthropic Claude API |
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Hosting | Render.com (via Procfile) |
| Statik fayllar | WhiteNoise |

---

## 4. Muhit o'zgaruvchilari (`.env`)

| O'zgaruvchi | Tavsif |
|-------------|--------|
| `SECRET_KEY` | Django maxfiy kalit |
| `DEBUG` | `True` / `False` |
| `DATABASE_URL` | PostgreSQL URL (bo'sh = SQLite) |
| `ANTHROPIC_API_KEY` | Claude AI uchun |
| `GOOGLE_CLIENT_ID/SECRET` | Google OAuth |
| `GITHUB_CLIENT_ID/SECRET` | GitHub OAuth |
| `EMAIL_HOST_USER/PASSWORD` | Gmail SMTP |

---

## 5. Custom Template Filterlar

`apps/templatetags/custom_filters.py`:

| Filter | Tavsif | Misol |
|--------|--------|-------|
| `split` | Stringni ajratadi | `"a,b,c"\|split:","` → `["a","b","c"]` |
| `strip` | Bo'shliqlarni olib tashlaydi | `" text "\|strip` → `"text"` |

---

## 6. Workspace Fayl Sinxronlash

Terminal buyruq yuborilganda:
1. `_sync_workspace_to_disk(workspace)` chaqiriladi
2. DB dagi barcha fayllar `workspaces/{pk}/` papkasiga yoziladi
3. Buyruq shu papkadan bajariladi
4. Natija terminalda ko'rsatiladi

---

## 7. Qo'llab-quvvatlanadigan til/run buyruqlar

| Kengaytma | Buyruq |
|-----------|--------|
| `.py` | `python "fayl.py"` |
| `.js` | `node "fayl.js"` |
| `.sh` | `bash "fayl.sh"` |

---

## 8. URLs strukturasi

```
/                          → Bosh sahifa
/auth/                     → Autentifikatsiya (allauth)
/feed/                     → Ijtimoiy feed
/dashboard/projects/       → Loyihalar ro'yxati
/dashboard/projects/<pk>/  → Loyiha tafsiloti
/workspace/<pk>/           → IDE workspace
/jobs/                     → Ish o'rinlari
/assets/                   → 3D aktivlar
/ai/explain-code/          → AI kod tushuntirish
/ai/generate-tasks/        → AI vazifa generatsiya
/admin/                    → Django admin
```

---

## 10. Tavsiya etilayotgan yaxshilanishlar (Roadmap)

### 10.1 Arxitektura va Refaktoring
- **Monolitik fayllarni ajratish**: `feed` va boshqa modullarda modellarni, URL-larni va Admin sozlamalarini `views.py` ichidan o'zining tegishli fayllariga (`models.py`, `urls.py`, `admin.py`) ko'chirish.
- **Service Layer**: Murakkab biznes logikani (masalan, workspace sinxronizatsiyasi) alohida `services.py` fayllariga chiqarish.
- **CSS Refaktoring**: `base.html` ichidagi barcha inline CSS-larni alohida `static/css/main.css` fayliga ko'chirish.

### 10.2 Real-time Imkoniyatlar
- **Django Channels**: Polling (vaqtinchalik so'rov yuborish) tizimini WebSocket-ga almashtirish (Chat, Bildirishnomalar va Workspace uchun).
- **Typing Indicators**: Chatda kimdir yozayotganini real-time ko'rsatish.

### 10.3 AI va Smart Funksiyalar
- **AI Debugger**: Workspace-da xatolarni aniqlash va avtomatik tuzatish taklif qilish.
- **3D Asset Previewer**: 3D modellarni (GLB/OBJ) brauzerning o'zida Three.js orqali ko'rish imkoniyati.
- **AI Code Review**: Pull Request-larni yoki saqlangan kodlarni AI orqali tekshirish.
- **Smart Search**: Oddiy qidiruvni PostgreSQL Full Text Search yoki Meilisearch-ga almashtirish.
- **3D Physics**: Studio ichida real-time fizika (Rapier.js/Cannon.js).
- **AI 3D Generation**: Matn orqali 3D model yaratish integratsiyasi.

### 10.4 Xavfsizlik va Barqarorlik
- **Terminal Sandbox**: Terminal buyruqlarini yanada chuqurroq cheklash (Docker containers orqali izolyatsiya qilish tavsiya etiladi).
- **Automated Testing**: `pytest` orqali unit va integratsion testlarni yozish.

---

## 11. O'zgarishlar tarixi

| Sana | Versiya | O'zgarish |
|------|---------|-----------|
| 2026-04-26 | 1.9 | 3D Studio Expansion: HDR, Fog, Advanced Materials, GLTF Export |
| 2026-04-24 | 1.8 | Escrow Job System, Secure Delivery (Preview-only), Private Offers |
| 2026-04-24 | 1.7 | Premium Features: 3D Previewer, AI Debugger, Heatmap, RT Notifications |
| 2026-04-24 | 1.6 | WebSocket integratsiyasi: Django Channels, Real-time Messaging & Typing Indicators |
| 2026-04-24 | 1.5 | PRD yangilandi: Roadmap va arxitektura takliflari qo'shildi |
| 2026-04-23 | 1.4 | Messaging Media (Rasm/Video/Fayl), Feed Video, Asset Cart (Savat) & Purchase |
| 2026-04-20 | 1.3 | Terminal Sandbox & Path Virtualization, Library Manager, Video Qo'ng'iroq (Jitsi) |
| 2026-04-08 | 1.2 | Template xatolari tuzatildi, custom_filters qo'shildi |
| 2026-04-08 | 1.1 | Workspace refactoring, Terminal sinxronlash, Run tugmasi |
| 2026-03-23 | 1.0 | Dastlabki ishga tushirish, workspace models ajratildi |
| 2026-04-26 | 2.0 | **Antigravity Review**: Arxitektura refaktoringi, xavfsizlik va mantiqiy xatolarni tuzatish boshlandi. |

---

## 12. Antigravity Audit (2026-04-26) - ✅ YAKUNLANDI

Loyiha ko'rib chiqildi va quyidagi muhim yaxshilanishlar amalga oshirildi:

1.  **Arxitektura**: `apps/feed` moduli Django standartiga muvofiq `models.py`, `urls.py`, `admin.py` va `views.py` ga ajratildi.
2.  **Middleware**: `SubscriptionMiddleware` dagi xavfli bazani boshqarish (migrations/SQL) amaliyotlari to'xtatildi va kod soddalashtirildi.
3.  **Performance**: `learn` modulidagi `progress_percent` hisoblanishi optimallashtirildi.
4.  **Mantiq**: Bildirishnomalardagi mantiqiy xatolar (`asset_liked` vs `post_liked`) va boshqa turlarni nomlashdagi xatolar tuzatildi.
5.  **Tozalash**: Funksiyalar ichidagi keraksiz lokal importlar yuqoriga ko'chirildi va kod tozaligi ta'minlandi.


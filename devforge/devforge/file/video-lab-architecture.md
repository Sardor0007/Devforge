# Web-based Video Tahrirchi (Video Lab) — To'liq Arxitektura Hujjati

> DevForge Studio Editor moduli uchun — Django 5 backend + JS frontend

---

## 1. Umumiy Arxitektura

Video tahrirlash rasm tahrirlashdan tubdan farq qiladi — chunki bu yerda **vaqt o'qi (timeline)**, **frame-by-frame rendering** va juda katta hajmdagi ma'lumot (har soniyada 24-60 frame) bilan ishlash kerak. Shu sabab arxitektura ikkiga bo'linadi: **preview (past-quality, real-time)** va **final render (yuqori sifat, server-side)**.

```
┌───────────────────────────────────────────────────────────┐
│                     BROWSER (Frontend)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Timeline      │  │ Preview       │  │ Effects/Transition│ │
│  │ Engine        │  │ Player        │  │ Editor            │ │
│  │ (tracks,      │  │ (Canvas/      │  │ (keyframe-based)  │ │
│  │  clips, cuts) │  │  WebCodecs)   │  │                   │ │
│  └──────┬───────┘  └──────┬───────┘  └────────┬──────────┘ │
│         └──────────┬───────┴──────────────────┘            │
│              Project State (EDL — Edit Decision List)       │
└────────────────────────┬────────────────────────────────── ┘
                          │ REST/WebSocket + chunked upload
┌─────────────────────────▼───────────────────────────────┐
│                  DJANGO BACKEND (Server)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Transcoding   │  │ Render Queue │  │ Storage/CDN     │ │
│  │ (FFmpeg)      │  │ (Celery +    │  │ (chunked video, │ │
│  │               │  │  GPU workers)│  │  thumbnails)    │ │
│  └──────────────┘  └──────────────┘  └────────────────┘ │
└───────────────────────────────────────────────────────── ┘
```

**Asosiy prinsip:** Brauzer hech qachon to'liq video faylni piksel darajasida qayta ishlamaydi (bu imkonsiz — juda og'ir). Frontend faqat **"nima qilish kerakligi" haqidagi ko'rsatmalar ro'yxatini (EDL)** yig'adi, past-sifatli preview ko'rsatadi, va yakuniy renderni serverga (FFmpeg) topshiradi.

---

## 2. EDL (Edit Decision List) — Loyihaning yuragi

Video tahrirchida rasm kabi "piksel state" saqlanmaydi — buning o'rniga **buyruqlar ro'yxati** saqlanadi:

```javascript
{
  timeline: {
    duration: 120.5, // soniya
    fps: 30,
    tracks: [
      {
        type: "video",
        clips: [
          {
            id: "clip_1",
            sourceFile: "raw_footage_1.mp4",
            trimStart: 2.3,      // manba fayldagi boshlanish
            trimEnd: 15.8,       // manba fayldagi tugash
            timelineStart: 0,     // timeline'dagi joylashuv
            speed: 1.0,
            transform: { scale: 1, x: 0, y: 0, rotation: 0 },
            effects: [ { type: "colorGrade", params: {...} } ]
          }
        ]
      },
      { type: "audio", clips: [...] },
      { type: "text/overlay", clips: [...] }
    ],
    transitions: [
      { betweenClips: ["clip_1", "clip_2"], type: "crossfade", duration: 0.5 }
    ]
  }
}
```

Bu yondashuvning afzalligi: **non-destructive** — original fayl hech qachon o'zgartirilmaydi, faqat "qanday ishlatish kerakligi" haqida metadata saqlanadi. Bu Premiere Pro, DaVinci Resolve kabi professional dasturlarning asosiy prinsipi.

---

## 3. Frontend: Timeline va Preview

### 3.1. Timeline Engine

Timeline — bu gorizontal chiziq bo'ylab clip'larni joylashtirish, kesish, siljitish uchun UI komponenti.

| Funksiya | Ishlash prinsipi |
|---|---|
| **Drag & drop clip** | Sichqoncha X-koordinatasi → vaqtga konvertatsiya (`time = x / pixelsPerSecond`) |
| **Trim (kesish)** | Clip chetidan tortish → `trimStart`/`trimEnd` yangilanadi |
| **Split (ikkiga bo'lish)** | Playhead turgan joyda clip ikkita mustaqil clip'ga bo'linadi |
| **Snap (magnit)** | Clip boshqa clip chetiga yoki playhead'ga yaqinlashganda avtomatik "yopishadi" |
| **Multi-track** | Video, audio, matn, overlay — alohida qatorlarda, bir-biriga bog'liq emas |
| **Zoom** | `pixelsPerSecond` qiymatini o'zgartirish orqali timeline'ni kattalashtirish/kichraytirish |

### 3.2. Preview Player — eng qiyin qismi

Brauzerda **real-time** ravishda bir nechta video clipni, effektlarni, o'tishlarni (transition) birlashtirib ko'rsatish kerak. Buning uchun ikki yondashuv bor:

**A) HTML5 `<video>` elementlar + Canvas compositing**
```javascript
// Har bir track uchun alohida <video> elementi, hidden holda
// Playhead vaqtiga qarab video.currentTime = timelineTime - clip.timelineStart + clip.trimStart
// Har frame'da barcha tracklarni Canvas'ga chizib, composite qilish
function renderFrame(time) {
  ctx.clearRect(0, 0, width, height);
  activeClips(time).forEach(clip => {
    const video = getVideoElement(clip);
    video.currentTime = mapToSourceTime(time, clip);
    ctx.globalAlpha = clip.opacity;
    ctx.drawImage(video, clip.transform.x, clip.transform.y);
  });
  requestAnimationFrame(() => renderFrame(playhead.time));
}
```
Bu usul — oddiy, lekin **frame-accurate emas** (video.currentTime o'zgarishi async va sekin bo'lishi mumkin).

**B) WebCodecs API (zamonaviy, tavsiya etiladi)**
Brauzerning past darajadagi video decode/encode API'si — har bir frame'ni alohida piksel bufferi sifatida olish imkonini beradi, bu **frame-perfect preview** beradi va GPU orqali tezroq ishlaydi. Chrome/Edge'da yaxshi qo'llab-quvvatlanadi, Safari'da qisman.

**Tavsiya:** Boshlashda (A) usuli bilan boshlash (tezroq implement qilinadi), keyinchalik WebCodecs'ga o'tish.

### 3.3. Effektlar va Keyframe tizimi

Har bir parametr (opacity, position, scale, color) vaqt bo'ylab o'zgarishi mumkin — bu **keyframe** orqali amalga oshiriladi:

```javascript
{
  property: "opacity",
  keyframes: [
    { time: 0, value: 0, easing: "easeIn" },
    { time: 1.5, value: 1, easing: "linear" },
    { time: 8, value: 1 },
    { time: 9, value: 0, easing: "easeOut" }
  ]
}
```

Berilgan vaqt uchun qiymat — ikki qo'shni keyframe orasida **interpolatsiya** (linear, ease-in/out, bezier) orqali hisoblanadi. Bu animatsiya (fade in/out, pan, zoom) asosini tashkil qiladi.

---

## 4. Backend (Django + FFmpeg): Og'ir ishlar

### 4.1. Nima uchun FFmpeg

FFmpeg — video/audio qayta ishlashning sanoat standarti. Django undan **subprocess** yoki `ffmpeg-python` kutubxonasi orqali foydalanadi:

```python
# services/video_processor.py
import ffmpeg

class VideoRenderer:
    def render_timeline(self, edl_json, output_path):
        """EDL asosida FFmpeg filter_complex grafigini quradi"""
        inputs = []
        filter_parts = []

        for i, clip in enumerate(edl_json["tracks"][0]["clips"]):
            stream = ffmpeg.input(
                clip["sourceFile"],
                ss=clip["trimStart"],
                to=clip["trimEnd"]
            )
            # Transform, speed, effektlarni qo'llash
            if clip.get("speed", 1.0) != 1.0:
                stream = stream.filter("setpts", f"{1/clip['speed']}*PTS")
            inputs.append(stream)

        # Barcha clip'larni concat yoki xtransition orqali birlashtirish
        joined = ffmpeg.concat(*inputs, v=1, a=1)
        out = ffmpeg.output(joined, output_path,
                             vcodec="libx264", acodec="aac",
                             preset="medium", crf=23)
        ffmpeg.run(out, overwrite_output=True)
```

### 4.2. Transkoding va Proxy fayllar

Foydalanuvchi 4K raw footage yuklaganda, uni to'g'ridan-to'g'ri brauzerda preview qilish og'ir. Shuning uchun:

1. Yuklangan zahoti Celery task orqali **past-sifatli "proxy" versiya** yaratiladi (720p, tez decode bo'ladigan H.264)
2. Frontend preview'da **proxy** fayl bilan ishlaydi (tez, silliq)
3. Yakuniy export'da **original yuqori sifatli fayl** ishlatiladi

```python
@shared_task
def create_proxy(video_id):
    video = VideoAsset.objects.get(id=video_id)
    ffmpeg.input(video.original_file.path).output(
        f"proxies/{video_id}_proxy.mp4",
        vf="scale=1280:-2", crf=28, preset="ultrafast"
    ).run()
```

### 4.3. Render Queue (Celery + GPU)

Yakuniy export — eng og'ir amal, daqiqalab davom etishi mumkin:

```python
@shared_task(bind=True)
def render_final_video(self, project_id):
    project = VideoProject.objects.get(id=project_id)
    renderer = VideoRenderer()

    # Progress bar uchun
    self.update_state(state="PROGRESS", meta={"percent": 0})

    renderer.render_timeline(
        project.edl_data,
        output_path=f"renders/{project_id}_final.mp4",
        progress_callback=lambda p: self.update_state(
            state="PROGRESS", meta={"percent": p}
        )
    )

    project.status = "completed"
    project.rendered_file = f"renders/{project_id}_final.mp4"
    project.save()

    # WebSocket orqali frontendga xabar
    notify_render_complete(project_id)
```

GPU-accelerated encoding uchun FFmpeg'da `h264_nvenc` (NVIDIA) yoki `h264_qsv` (Intel) kabi hardware encoder ishlatish CPU'dan 5-10x tezroq.

---

## 5. Audio-Video sinxronizatsiya

Bu — video tahrirchidagi eng ko'p xato beruvchi joy. Asosiy qoidalar:

- Har bir clip **timebase** (masalan 30fps, 25fps) ga ega bo'lishi kerak, va timeline umumiy timebase'ga normalizatsiya qilinadi
- Audio waveform preview uchun oldindan hisoblanadi (Web Audio API `AudioContext.decodeAudioData` orqali) va statik rasm sifatida keshlanadi
- Frame-accurate trim uchun `trimStart`/`trimEnd` har doim **frame raqami** (vaqt emas) sifatida saqlanishi tavsiya etiladi: `frameNumber = Math.round(time * fps)`

---

## 6. Ma'lumot oqimi (Data Flow)

```
1. Foydalanuvchi video yuklaydi (chunked upload — katta fayllar uchun)
        │
        ▼
2. Celery: original saqlanadi + proxy (720p) yaratiladi + thumbnail'lar generatsiya qilinadi
        │
        ▼
3. Frontend: Timeline'ga clip qo'shiladi, proxy bilan preview ko'rsatiladi
        │
        ▼
4. Foydalanuvchi trim, split, effekt, keyframe qo'shadi
   → Barchasi EDL (JSON) formatida frontend state'da saqlanadi
        │
        ▼
5. Auto-save: EDL Django'ga yuboriladi (faqat metadata, video emas)
        │
        ▼
6. "Export" bosilganda: to'liq EDL serverga yuboriladi
   → Celery task → FFmpeg orqali original fayllardan yakuniy video render qilinadi
   → Progress WebSocket orqali frontendga uzatiladi (%)
   → Tayyor bo'lgach yuklab olish link'i beriladi
```

---

## 7. Tavsiya etilgan texnologik stack

```
Frontend:
  - Custom Timeline UI (React + Canvas) yoki Remotion (React-based video framework)
  - WebCodecs API — frame-accurate preview (progressive enhancement)
  - Web Audio API — waveform vizualizatsiya
  - Chunked upload (tus.io protokoli) — katta video fayllar uchun

Backend (Django, mavjud stackingga mos):
  - FFmpeg (subprocess yoki ffmpeg-python) — transcoding, rendering
  - Celery + Redis — render queue, progress tracking
  - django-storages + S3/CDN — video fayllarni saqlash va uzatish
  - Django Channels — render progress uchun real-time xabar
  - GPU worker (NVENC/QSV) — tezroq encoding (ixtiyoriy, katta yuklamada foydali)

Ixtiyoriy AI qo'shimchalar:
  - Whisper (OpenAI) — avtomatik subtitrlash/transkripsiya
  - RIFE/FILM — frame interpolation (sekin harakat effektlari)
  - Auto scene detection (PySceneDetect) — avtomatik kesish nuqtalarini topish
```

---

## 8. Bosqichma-bosqich rivojlantirish rejasi

**1-bosqich (MVP):**
- Video yuklash, bitta track'da timeline
- Trim, split, playhead bilan preview (HTML5 video asosida)
- Oddiy export (FFmpeg concat)

**2-bosqich:**
- Multi-track (video + audio + matn)
- Transition'lar (crossfade, cut)
- Proxy fayl tizimi (tez preview uchun)
- Progress bar bilan async render (Celery)

**3-bosqich:**
- Keyframe-based effektlar (fade, pan, zoom, color grading)
- Audio waveform, ovoz balandligini sozlash
- Text/overlay editor (subtitr, unvon)

**4-bosqich (professional):**
- WebCodecs bilan frame-accurate preview
- AI funksiyalar (auto-subtitle, scene detection)
- GPU-accelerated render
- Real-time hamkorlik (bir loyihada bir nechta odam)

---

## 9. Xulosa

Video tahrirlashning asosiy printsipi: **frontend hech qachon "haqiqiy" video ma'lumotni og'ir qayta ishlamaydi — u faqat ko'rsatmalar (EDL) yig'adi va past-sifatli preview ko'rsatadi.** Yakuniy, sifatli natija — har doim serverda, FFmpeg orqali, asinxron (Celery) tarzda tayyorlanadi. Bu arxitektura professional video tahrirchilarning (Premiere, DaVinci, CapCut Web) barchasida qo'llaniladigan asosiy naqsh hisoblanadi.

# Web-based Rasm Tahrirchi — To'liq Arxitektura Hujjati

> DevForge Studio Editor moduli uchun (Image Editor) — Django 5 backend + JS frontend

---

## 1. Umumiy Arxitektura

Zamonaviy web rasm tahrirchisi ikki qatlamda ishlaydi:

```
┌─────────────────────────────────────────────────────────┐
│                     BROWSER (Frontend)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Canvas Engine │  │ Tool System  │  │ History/Undo    │ │
│  │ (Fabric.js/   │  │ (Brush, Crop,│  │ (Command Stack) │ │
│  │  Konva/WebGL) │  │  Select, etc)│  │                 │ │
│  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘ │
│         └──────────┬───────┴──────────────────┘          │
│                State Manager (Layers, Selection)          │
└────────────────────────┬───────────────────────────────  ┘
                          │ REST/WebSocket
┌─────────────────────────▼───────────────────────────────┐
│                  DJANGO BACKEND (Server)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Image Process │  │ File Storage │  │ Export/Render   │ │
│  │ (Pillow/      │  │ (S3/local +  │  │ Pipeline        │ │
│  │  OpenCV)      │  │  versioning) │  │ (Celery async)  │ │
│  └──────────────┘  └──────────────┘  └────────────────┘ │
└───────────────────────────────────────────────────────── ┘
```

**Muhim qaror:** Real-time tahrirlash (filtr preview, kadrlash, chizish) — **client-side (Canvas/WebGL)** da bo'lishi kerak, aks holda har bir amal uchun serverga so'rov yuborish sekin va qimmat bo'ladi. Server esa **og'ir amallar** (yakuniy export, AI-filtrlar, katta rasmlarni qayta ishlash, format konversiya) uchun ishlatiladi.

---

## 2. Frontend: Canvas Engine tanlash

| Kutubxona | Nima uchun yaxshi | Cheklovlari |
|---|---|---|
| **Fabric.js** | Layer, selection, transform tayyor holda bor. O'rganish oson. | Katta rasmlarda (4K+) sekinlashadi |
| **Konva.js** | Yuqori performance, React bilan yaxshi integratsiya (react-konva) | Ba'zi murakkab filtrlar uchun qo'lda yozish kerak |
| **Raw Canvas API + WebGL** | To'liq nazorat, eng tez ishlash | Hammasini noldan yozish kerak (ko'p vaqt) |
| **Pixi.js** | WebGL asosida, GPU tezlikda filtrlar | O'rganish egri chizig'i baland |

**Tavsiya:** Boshlash uchun **Konva.js** (yoki React bilan ishlasang **react-konva**) — u layer tizimi, transform, event handling'ni tayyor beradi, va GPU-accelerated rendering ishlatadi.

---

## 3. Asosiy funksional bloklar

### 3.1. Layer System (Qatlamlar tizimi)

Har bir rasm — bu qatlamlar stack'i:

```javascript
{
  id: "layer_1",
  type: "image" | "text" | "shape" | "adjustment",
  visible: true,
  opacity: 1.0,
  blendMode: "normal" | "multiply" | "screen" | ...,
  transform: { x, y, scaleX, scaleY, rotation },
  data: <canvas/image reference>,
  locked: false,
  zIndex: 0
}
```

Rendering paytida qatlamlar pastdan yuqoriga qarab, `blendMode` va `opacity` hisobga olinib composite qilinadi (bu ishni Canvas `globalCompositeOperation` yoki WebGL shader orqali qilish mumkin).

### 3.2. Tool System (Asboblar)

| Tool | Ishlash prinsipi |
|---|---|
| **Selection (Marquee, Lasso)** | Sichqoncha koordinatalarini yig'ib, path/rectangle yaratadi → shu path asosida piksel maskasi hosil bo'ladi |
| **Crop** | Tanlangan hudud tashqarisidagi canvas'ni kesib tashlaydi, transform matritsani yangilaydi |
| **Brush/Pencil** | Har mouse-move eventida nuqta qo'shiladi, nuqtalar orasida chiziq (stroke) chiziladi. Bosim (pressure) — Pointer Events API orqali |
| **Eraser** | `globalCompositeOperation = "destination-out"` bilan piksellarni shaffof qiladi |
| **Text** | HTML overlay yoki Canvas `fillText` — font, size, color, alignment |
| **Shape (rect, circle, line)** | Vektor primitivlar, keyin rasterize qilinadi yoki vektor holda saqlanadi |
| **Fill (bucket)** | Flood-fill algoritmi — bir xil rangdagi qo'shni piksellarni topib, yangi rang bilan to'ldiradi |
| **Eyedropper** | Bosilgan piksel koordinatasidan RGB qiymatini o'qiydi |
| **Clone Stamp** | Manba nuqtadan piksellarni nusxalab, boshqa joyga chizadi (offset saqlanadi) |

### 3.3. Adjustment / Filter Tizimi

Ikki xil yondashuv bor:

1. **Piksel-based (destructive)** — filtr darhol piksel qiymatlariga qo'llaniladi, orqaga qaytarish faqat Undo orqali
2. **Adjustment Layer (non-destructive)** — filtr alohida qatlam sifatida saqlanadi, istalgan vaqt o'zgartirish/o'chirish mumkin (professional tahrirchilar — Photoshop, Figma shu usulni ishlatadi)

**Tavsiya:** Non-destructive yondashuvni tanlash — bu murakkabroq, lekin foydalanuvchi tajribasi ancha yaxshi bo'ladi.

Asosiy filtrlar matematikasi:

```
Brightness:  new_pixel = old_pixel + value
Contrast:    new_pixel = (old_pixel - 128) * factor + 128
Saturation:  HSL formatga o'tkazib, S kanalini o'zgartirish
Blur:        Gaussian convolution kernel (3x3, 5x5, 7x7)
Sharpen:     Unsharp mask (original - blurred versiya farqini kuchaytirish)
Grayscale:   gray = 0.299*R + 0.587*G + 0.114*B
Invert:      new = 255 - old
```

Katta rasmlar uchun bu amallarni **WebGL shader** (GPU) orqali qilish CPU'dan 10-50x tezroq bo'ladi.

### 3.4. History / Undo-Redo

**Command Pattern** ishlatiladi — har bir amal (`AddLayerCommand`, `MoveCommand`, `FilterCommand`) `execute()` va `undo()` metodlariga ega:

```javascript
class Command {
  execute() { /* amalni bajarish */ }
  undo() { /* orqaga qaytarish */ }
}

class HistoryManager {
  stack = [];
  pointer = -1;

  do(command) {
    command.execute();
    this.stack = this.stack.slice(0, this.pointer + 1);
    this.stack.push(command);
    this.pointer++;
  }

  undo() { this.stack[this.pointer--].undo(); }
  redo() { this.stack[++this.pointer].execute(); }
}
```

Katta rasmlar uchun har bir state'ni to'liq saqlash xotira yeydi — shuning uchun **diff-based** (faqat o'zgargan qismini saqlash) yoki **snapshot throttling** (har N amalda bitta to'liq snapshot) qo'llash kerak.

---

## 4. Backend (Django): Nima uchun kerak

| Vazifa | Nega server kerak |
|---|---|
| **Export** (PNG/JPEG/WebP/PDF yuklab olish) | Katta o'lchamli, yuqori sifatli export — brauzer xotirasini yeb qo'yishi mumkin |
| **AI filtrlar** (background remove, upscale, style transfer) | Og'ir ML model — GPU kerak, brauzerda ishlamaydi |
| **Format konversiya** | RAW, TIFF, PSD kabi murakkab formatlar |
| **Fayl saqlash/versiyalash** | Loyihalarni saqlash, tarixni saqlash |
| **Katta rasmlarni qayta ishlash** (masalan 8000x8000px) | Client xotira cheklovi |

### Django implementatsiyasi

```python
# models.py
class ImageProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    canvas_data = models.JSONField()  # layers, transforms — Fabric/Konva JSON
    thumbnail = models.ImageField(upload_to='thumbnails/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ImageLayer(models.Model):
    project = models.ForeignKey(ImageProject, related_name='layers', on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='layers/')
    order = models.IntegerField()
```

```python
# services/image_processor.py — Pillow/OpenCV bilan og'ir amallar
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import numpy as np

class ImageProcessor:
    def apply_filter(self, image_path, filter_type, params):
        img = Image.open(image_path)
        if filter_type == "blur":
            return img.filter(ImageFilter.GaussianBlur(params.get("radius", 5)))
        elif filter_type == "sharpen":
            return img.filter(ImageFilter.SHARPEN)
        elif filter_type == "brightness":
            return ImageEnhance.Brightness(img).enhance(params.get("factor", 1.2))
        # ...

    def remove_background(self, image_path):
        # rembg yoki U-2-Net kabi model orqali
        pass

    def export_final(self, project, format="png", quality=95):
        # Barcha qatlamlarni composite qilib, yakuniy faylni yaratish
        pass
```

Og'ir amallar (AI filtrlar, katta export) — **Celery + Redis** orqali asinxron bajarilishi kerak, aks holda foydalanuvchi brauzeri "osilib qoladi":

```python
# tasks.py
from celery import shared_task

@shared_task
def process_ai_filter(project_id, filter_type, params):
    project = ImageProject.objects.get(id=project_id)
    processor = ImageProcessor()
    result = processor.apply_filter(project.image_file.path, filter_type, params)
    result.save(f"media/processed/{project_id}_result.png")
    # WebSocket orqali frontendga tayyor bo'lganini xabar berish
```

---

## 5. Ma'lumot oqimi (Data Flow)

```
1. Foydalanuvchi rasm yuklaydi
        │
        ▼
2. Frontend: Canvas'ga image sifatida yuklanadi (client-side)
        │
        ▼
3. Foydalanuvchi tool ishlatadi (brush, crop, filter preview)
   → Bularning barchasi Canvas/WebGL'da REAL-TIME, serverga so'rovsiz
        │
        ▼
4. Har amal HistoryManager'ga Command sifatida qo'shiladi (Undo/Redo)
        │
        ▼
5. Auto-save: har necha soniyada canvas JSON holati Django'ga yuboriladi
   (faqat state, rasm emas — layer transform, filter parametrlari)
        │
        ▼
6. Export bosilganda: to'liq canvas state + original rasm(lar) serverga
   yuboriladi → Pillow/OpenCV bilan yuqori sifatli final render → 
   Celery task → tayyor bo'lgach WebSocket orqali link qaytariladi
```

---

## 6. WebSocket integratsiyasi (real-time hamkorlik uchun)

DevForge'da Django Channels allaqachon bor ekan (WebRTC uchun ishlatgansan) — shuni Image Editor uchun ham ishlatish mumkin:

- Bir nechta foydalanuvchi bitta loyihada bir vaqtda ishlashi (Figma-style)
- Har bir layer o'zgarishi boshqa foydalanuvchilarga broadcast qilinadi
- Conflict resolution uchun **Operational Transform** yoki oddiyroq **"last-write-wins per layer"** strategiyasi

```python
# consumers.py
class ImageEditorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.group_name = f"project_{self.project_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        # layer o'zgarishini boshqa clientlarga yuborish
        await self.channel_layer.group_send(self.group_name, {
            "type": "layer_update",
            "data": data
        })
```

---

## 7. Xotira va Performance strategiyasi

| Muammo | Yechim |
|---|---|
| Katta rasm (4K+) brauzerni sekinlashtiradi | Preview uchun kichraytirilgan versiya (downscaled) ishlatish, faqat export'da original |
| Har bir filtr preview'ida to'liq qayta chizish | Debounce/throttle qo'llash (masalan 100ms), yoki faqat ko'rinayotgan hudud (viewport) render qilish |
| Ko'p layer — sekin composite | Offscreen canvas'da oldindan compositing, keshlash |
| Undo stack xotira yeydi | Snapshot o'rniga diff saqlash, yoki stack chuqurligini cheklash (masalan 50 ta amal) |
| Filtrlar CPU'ni band qiladi | Web Worker'da hisoblash (main thread bloklanmasligi uchun) yoki WebGL shader |

---

## 8. Tavsiya etilgan texnologik stack (DevForge uchun)

```
Frontend:
  - Konva.js yoki Fabric.js — canvas/layer boshqaruvi
  - Web Workers — og'ir filtr hisoblari uchun
  - IndexedDB — lokal auto-save (internet uzilganda ham yo'qolmasligi uchun)

Backend (Django, mavjud stackingga mos):
  - Django REST Framework — API
  - Pillow — asosiy rasm amallari
  - OpenCV-python — murakkabroq computer vision (edge detection, va h.k.)
  - Celery + Redis — asinxron og'ir vazifalar (AI filtr, export)
  - Django Channels — real-time hamkorlik (WebSocket)
  - django-storages + S3 (yoki local) — fayl saqlash

Ixtiyoriy AI qo'shimchalar:
  - rembg — background remove
  - Real-ESRGAN — rasm sifatini oshirish (upscale)
  - Stable Diffusion API — style transfer / generativ tahrirlash
```

---

## 9. Bosqichma-bosqich rivojlantirish rejasi (MVP → Full)

**1-bosqich (MVP):**
- Rasm yuklash, Canvas'da ko'rsatish
- Crop, rotate, flip
- Asosiy filtrlar (brightness, contrast, saturation, grayscale)
- Export (PNG/JPEG)

**2-bosqich:**
- Layer tizimi (qo'shish, o'chirish, tartiblash, opacity)
- Brush/Eraser/Text/Shape tool'lari
- Undo/Redo (Command pattern)
- Auto-save (Django'ga JSON state)

**3-bosqich:**
- Adjustment layers (non-destructive)
- Advanced filtrlar (blur, sharpen, HSL curves)
- Selection tools (lasso, magic wand)

**4-bosqich (professional):**
- AI-powered funksiyalar (background remove, upscale)
- Real-time hamkorlik (WebSocket)
- Template/preset tizimi
- Katta fayl performance optimizatsiyasi (WebGL, Web Workers)

---

## 10. Xulosa

Asosiy prinsip: **"Client tez ishlaydi, server aqlli ishlaydi."** Foydalanuvchi tajribasi uchun barcha interaktiv amallar (chizish, kadrlash, preview) — brauzerda, Canvas/WebGL orqali, kechikishsiz bo'lishi kerak. Server esa faqat og'ir, murakkab, yoki saqlash talab qiladigan ishlarni (yakuniy export, AI, fayl versiyalash) bajaradi.

DevForge kontekstida bu modul alohida Django app (`image_editor`) sifatida qo'shilishi, va mavjud loyiha/workspace tizimiga integratsiya qilinishi mumkin — foydalanuvchi loyihasi ichida to'g'ridan-to'g'ri rasm ustida ishlay oladi.

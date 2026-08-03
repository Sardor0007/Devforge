# Web-based Audio Tahrirchi (Audio Lab) — To'liq Arxitektura Hujjati

> DevForge Studio Editor moduli uchun — Django 5 backend + JS frontend

---

## 1. Umumiy Arxitektura

Audio tahrirlash video/rasmga qaraganda "yengilroq" ma'lumot bilan ishlaydi (1D signal, 2D piksel emas), lekin **real-time signal processing** va **aniq vaqt sinxronizatsiyasi** talab qiladi. Bu yerda asosiy kuch — **Web Audio API**, brauzerning o'rnatilgan audio dvigateli.

```
┌───────────────────────────────────────────────────────────┐
│                     BROWSER (Frontend)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Multitrack    │  │ Web Audio API │  │ Effects Chain     │ │
│  │ Timeline      │  │ Audio Graph   │  │ (EQ, Compressor,  │ │
│  │ (clips,       │  │ (real-time    │  │  Reverb, Filter)  │ │
│  │  regions)     │  │  playback)    │  │                   │ │
│  └──────┬───────┘  └──────┬───────┘  └────────┬──────────┘ │
│         └──────────┬───────┴──────────────────┘            │
│           Project State (tracks, regions, automation)       │
└────────────────────────┬────────────────────────────────── ┘
                          │ REST/WebSocket
┌─────────────────────────▼───────────────────────────────┐
│                  DJANGO BACKEND (Server)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Rendering     │  │ AI Processing│  │ Storage         │ │
│  │ (FFmpeg/      │  │ (noise remove│  │ (audio fayllar, │ │
│  │  SoX mixdown) │  │  stem split) │  │  waveform cache)│ │
│  └──────────────┘  └──────────────┘  └────────────────┘ │
└───────────────────────────────────────────────────────── ┘
```

**Muhim jihat:** Rasm va videodan farqli o'laroq, audio uchun brauzerda **haqiqiy real-time processing** to'liq mumkin — Web Audio API GPU emas, lekin optimallashtirilgan native audio dvigatel orqali ishlaydi, va kechikish millisekundlarda o'lchanadi. Shu sabab ko'p effektlarni (EQ, kompressiya, reverb) **client-side'da jonli** eshitish mumkin, faqat yakuniy export/mixdown serverda.

---

## 2. Web Audio API — Asosiy tushuncha

Web Audio API — bu **audio graph** (node'lar tarmog'i) orqali ishlaydi. Har bir node — signalni qayta ishlovchi blok:

```javascript
const audioContext = new AudioContext();

// Signal yo'li: source → gain → EQ → compressor → destination (speakers)
const source = audioContext.createBufferSource();
const gainNode = audioContext.createGain();
const eq = audioContext.createBiquadFilter();
const compressor = audioContext.createDynamicsCompressor();

source.connect(gainNode);
gainNode.connect(eq);
eq.connect(compressor);
compressor.connect(audioContext.destination);
```

Bu graph — modulyar sintezatorlarga o'xshaydi: har bir effekt alohida "quti", ular ketma-ket yoki parallel ulanadi. Multitrack tahrirchida har bir track o'zining audio graph zanjiriga ega bo'ladi, va barchasi bitta **master bus**'ga yig'iladi.

---

## 3. Asosiy funksional bloklar

### 3.1. Multitrack Timeline

```javascript
{
  tracks: [
    {
      id: "track_1",
      name: "Vocal",
      regions: [
        {
          id: "region_1",
          sourceFile: "vocal_take1.wav",
          trimStart: 0.5, trimEnd: 12.3,
          timelineStart: 0,
          gain: 1.0,
          fadeIn: 0.1, fadeOut: 0.2,
          muted: false
        }
      ],
      volume: 0.8,
      pan: 0,        // -1 (chap) dan +1 (o'ng) gacha
      solo: false,
      mute: false,
      effects: [ { type: "eq", params: {...} }, { type: "compressor", params: {...} } ]
    }
  ],
  masterEffects: [ { type: "limiter", params: {...} } ]
}
```

Har bir **region** (audio fayl bo'lagi) — Video Lab'dagi "clip" konseptiga o'xshash: manba fayl, kesish nuqtalari, va timeline'dagi joylashuv saqlanadi (non-destructive).

### 3.2. Waveform Vizualizatsiya

Foydalanuvchi audio to'lqin shaklini ko'rishi kerak — bu ikki bosqichda amalga oshiriladi:

1. **Decode:** `audioContext.decodeAudioData()` orqali fayl PCM sample'larga aylantiriladi
2. **Downsample + chizish:** Millionlab sample'ni ekranga chizish imkonsiz, shuning uchun har necha sample uchun min/max qiymat olinadi (peak detection) va Canvas'ga chiziladi:

```javascript
function drawWaveform(audioBuffer, canvasWidth) {
  const data = audioBuffer.getChannelData(0); // birinchi kanal
  const samplesPerPixel = Math.floor(data.length / canvasWidth);
  const peaks = [];

  for (let i = 0; i < canvasWidth; i++) {
    let min = 1.0, max = -1.0;
    for (let j = 0; j < samplesPerPixel; j++) {
      const sample = data[i * samplesPerPixel + j];
      if (sample < min) min = sample;
      if (sample > max) max = sample;
    }
    peaks.push({ min, max });
  }
  return peaks; // Canvas'da har pixel uchun vertikal chiziq chizish uchun
}
```

Katta fayllar uchun bu hisoblashni **Web Worker**'da bajarish kerak (main thread'ni bloklamaslik uchun), va natijani keshlab qo'yish (qayta hisoblamaslik uchun).

### 3.3. Effektlar (Built-in Web Audio Node'lar)

| Effekt | Web Audio Node | Vazifasi |
|---|---|---|
| **EQ (Equalizer)** | `BiquadFilterNode` (bir nechtasi zanjirlanadi — low-shelf, peaking, high-shelf) | Ma'lum chastota diapazonini kuchaytirish/pasaytirish |
| **Compressor** | `DynamicsCompressorNode` | Baland/past ovoz farqini kamaytirish (dinamikani tekislash) |
| **Reverb** | `ConvolverNode` (impulse response fayl bilan) | Xona akustikasi effekti |
| **Delay/Echo** | `DelayNode` + feedback loop (`GainNode` orqali) | Aks-sado effekti |
| **Pan** | `StereoPannerNode` | Chap/o'ng balans |
| **Gain/Volume** | `GainNode` | Ovoz balandligi |
| **Filter (low-pass, high-pass)** | `BiquadFilterNode` | Ma'lum chastotadan yuqori/pastini kesish |
| **Limiter** | `DynamicsCompressorNode` (yuqori ratio bilan) | Signal clipping'dan himoya (master bus'da) |

Murakkabroq effektlar (pitch shift, time-stretch, noise reduction) — Web Audio'da tayyor node yo'q, shuning uchun **AudioWorklet** (custom DSP kodi) yoki server-side processing kerak bo'ladi.

### 3.4. AudioWorklet — Custom DSP

Real-time, past-latency custom audio processing uchun (masalan noise gate, custom distortion):

```javascript
// noise-gate-processor.js (alohida thread'da ishlaydi)
class NoiseGateProcessor extends AudioWorkletProcessor {
  process(inputs, outputs, parameters) {
    const input = inputs[0][0];
    const output = outputs[0][0];
    const threshold = parameters.threshold[0] || 0.01;

    for (let i = 0; i < input.length; i++) {
      output[i] = Math.abs(input[i]) < threshold ? 0 : input[i];
    }
    return true;
  }
}
registerProcessor('noise-gate', NoiseGateProcessor);
```

AudioWorklet — alohida audio thread'da ishlaydi (main JS thread'dan mustaqil), shu sabab UI qotib qolmaydi va audio kechikishi minimal bo'ladi.

### 3.5. Automation (Vaqt bo'ylab parametr o'zgarishi)

Video Lab'dagi keyframe konseptiga o'xshash — volume, pan kabi parametrlar vaqt bo'ylab o'zgarishi mumkin:

```javascript
// Web Audio API'ning o'rnatilgan automation tizimi
gainNode.gain.setValueAtTime(1.0, 0);
gainNode.gain.linearRampToValueAtTime(0.0, 5.0); // 5 soniyada fade-out
```

Bu — `AudioParam` interfeysi orqali sample-accurate aniqlikda ishlaydi (JS timer'ga bog'liq emas, shuning uchun juda aniq).

---

## 4. Backend (Django): Og'ir va AI ishlar

### 4.1. Mixdown/Export (SoX yoki FFmpeg)

Yakuniy export'da barcha tracklar, effektlar, automation'lar birlashtirilib bitta fayl (yoki stem'lar) yaratiladi:

```python
# services/audio_processor.py
import ffmpeg

class AudioRenderer:
    def mixdown(self, project_edl, output_path, format="wav"):
        inputs = []
        for track in project_edl["tracks"]:
            for region in track["regions"]:
                stream = ffmpeg.input(
                    region["sourceFile"],
                    ss=region["trimStart"], to=region["trimEnd"]
                )
                # Gain, fade, EQ kabi effektlarni FFmpeg audio filter orqali qo'llash
                stream = stream.filter("volume", track["volume"])
                if region.get("fadeIn"):
                    stream = stream.filter("afade", t="in", d=region["fadeIn"])
                inputs.append(stream)

        mixed = ffmpeg.filter(inputs, "amix", inputs=len(inputs))
        ffmpeg.output(mixed, output_path, acodec="pcm_s16le" if format == "wav" else "libmp3lame").run()
```

### 4.2. AI-powered funksiyalar (Celery orqali async)

| Funksiya | Model/Kutubxona |
|---|---|
| **Noise reduction** | `noisereduce` (Python), yoki RNNoise | Fon shovqinini olib tashlash |
| **Stem separation** (vokal/instrumentalga ajratish) | Demucs, Spleeter | Bitta audio faylni alohida qatlamlarga ajratish |
| **Auto-transcription** (matnga aylantirish) | OpenAI Whisper | Subtitr, lyrics generatsiyasi |
| **Mastering (avtomatik)** | Matchering yoki custom DSP zanjiri | Professional darajadagi yakuniy ovoz sifati |
| **Pitch/Tempo correction** | Rubber Band Library, pyrubberband | Ovoz balandligi/tezligini o'zgartirish sifat yo'qotmasdan |

```python
@shared_task
def remove_noise(audio_id):
    audio = AudioAsset.objects.get(id=audio_id)
    import noisereduce as nr
    import soundfile as sf

    data, rate = sf.read(audio.file.path)
    reduced = nr.reduce_noise(y=data, sr=rate)
    sf.write(f"processed/{audio_id}_clean.wav", reduced, rate)

    audio.processed_file = f"processed/{audio_id}_clean.wav"
    audio.save()
    notify_processing_complete(audio_id)
```

### 4.3. Waveform Pre-generation

Katta audio fayllar uchun waveform'ni har safar brauzerda hisoblash o'rniga, yuklangan zahoti serverda hisoblab, JSON sifatida saqlash tavsiya etiladi:

```python
@shared_task
def generate_waveform_data(audio_id):
    audio = AudioAsset.objects.get(id=audio_id)
    import librosa
    y, sr = librosa.load(audio.file.path, sr=None)
    # 1000 nuqtaga downsample qilish (frontend uchun yetarli)
    peaks = compute_peaks(y, num_points=1000)
    audio.waveform_data = json.dumps(peaks)
    audio.save()
```

---

## 5. Ma'lumot oqimi (Data Flow)

```
1. Foydalanuvchi audio fayl yuklaydi (WAV/MP3/FLAC)
        │
        ▼
2. Celery: waveform hisoblanadi, metadata (duration, sample rate) olinadi
        │
        ▼
3. Frontend: Web Audio API orqali fayl decode qilinadi, timeline'ga region qo'shiladi
        │
        ▼
4. Foydalanuvchi trim, fade, effekt qo'shadi
   → Real-time eshitish: Web Audio graph orqali (kechikishsiz preview)
   → Barcha o'zgarishlar EDL (JSON) sifatida saqlanadi
        │
        ▼
5. Auto-save: EDL Django'ga yuboriladi
        │
        ▼
6. "Export" bosilganda: EDL serverga yuboriladi
   → Celery task → FFmpeg/SoX orqali yakuniy mixdown
   → (ixtiyoriy) AI mastering/normalize
   → Tayyor fayl WebSocket orqali xabar bilan qaytariladi
```

---

## 6. Tavsiya etilgan texnologik stack

```
Frontend:
  - Web Audio API — real-time audio graph, effektlar
  - AudioWorklet — custom DSP (noise gate, custom effektlar)
  - Wavesurfer.js — tayyor waveform vizualizatsiya kutubxonasi (vaqtni tejaydi)
  - Web Worker — waveform hisoblash, katta fayllarni decode qilish

Backend (Django, mavjud stackingga mos):
  - FFmpeg / SoX — mixdown, format konversiya
  - librosa (Python) — audio analiz, waveform generatsiya
  - noisereduce, Demucs — AI audio processing
  - Celery + Redis — async render, AI processing queue
  - Django Channels — progress xabarlari

Ixtiyoriy AI qo'shimchalar:
  - OpenAI Whisper — auto-transcription/subtitr
  - Demucs/Spleeter — vokal-instrumental ajratish
  - Matchering — avtomatik mastering
```

---

## 7. Bosqichma-bosqich rivojlantirish rejasi

**1-bosqich (MVP):**
- Audio yuklash, waveform ko'rsatish
- Bitta track, trim/cut
- Play/pause, oddiy export

**2-bosqich:**
- Multitrack (vocal, instrumental, effektlar uchun alohida qatorlar)
- Volume, pan, mute/solo
- Fade in/out, region'larni siljitish

**3-bosqich:**
- EQ, Compressor, Reverb kabi effekt zanjiri (real-time preview bilan)
- Automation (vaqt bo'ylab volume/pan o'zgarishi)
- AudioWorklet orqali custom effektlar

**4-bosqich (professional):**
- AI funksiyalar (noise reduction, stem separation, auto-transcription)
- Avtomatik mastering
- Real-time hamkorlik

---

## 8. Xulosa

Audio tahrirlashning kuchli tomoni — **Web Audio API brauzerda haqiqiy real-time signal processing imkonini beradi**, shuning uchun rasm/video'dan farqli o'laroq ko'p effektni foydalanuvchi to'g'ridan-to'g'ri, kechikishsiz eshitib ko'ra oladi. Server esa asosan **yakuniy yuqori-sifatli export** va **AI-based murakkab funksiyalar** (noise reduction, stem separation) uchun ishlatiladi. Bu — DevForge'dagi Video Lab bilan juda o'xshash arxitekturaga ega (EDL, Celery render queue), shuning uchun ikkalasi orasida umumiy backend infratuzilmani (Celery worker, storage) baham ko'rish mumkin.

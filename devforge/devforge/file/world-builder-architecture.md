# Web-based Dunyo Yaratish Muharriri (World Builder) — To'liq Arxitektura Hujjati

> DevForge Studio Editor moduli uchun — Django 5 backend + JS frontend (Three.js/WebGL)

---

## 1. Umumiy Arxitektura

World Builder — DevForge'dagi eng murakkab modul, chunki u **3D fazoda real-time rendering, katta hajmdagi geometrik ma'lumot va asset boshqaruvi**ni birlashtiradi. Bu modul aslida — brauzerda ishlaydigan kichik "game engine editor" (Unity/Unreal Editor'ning soddalashtirilgan web versiyasi).

```
┌───────────────────────────────────────────────────────────┐
│                     BROWSER (Frontend)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ 3D Viewport   │  │ Scene Graph   │  │ Asset/Inspector   │ │
│  │ (Three.js/    │  │ (hierarchy,   │  │ Panel              │ │
│  │  WebGL)       │  │  transforms)  │  │ (properties, mat)  │ │
│  └──────┬───────┘  └──────┬───────┘  └────────┬──────────┘ │
│         └──────────┬───────┴──────────────────┘            │
│         World State (entities, terrain, lighting, physics)  │
└────────────────────────┬────────────────────────────────── ┘
                          │ REST/WebSocket
┌─────────────────────────▼───────────────────────────────┐
│                  DJANGO BACKEND (Server)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Asset Pipeline│  │ World Storage│  │ Export/Bake     │ │
│  │ (model import,│  │ (scene JSON, │  │ (Unity/Godot    │ │
│  │  optimization)│  │  versioning) │  │  format export) │ │
│  └──────────────┘  └──────────────┘  └────────────────┘ │
└───────────────────────────────────────────────────────── ┘
```

**Asosiy farq boshqa tahrirchilardan:** World Builder'da rendering **to'liq client-side, GPU orqali (WebGL/WebGPU)** bo'ladi — bu yerda server "rasm chizmaydi", faqat **ma'lumotni saqlaydi, asset'larni optimallashtiradi va export qiladi**.

---

## 2. Scene Graph — Dunyoning ma'lumot tuzilmasi

3D dunyo — bu **ierarxik daraxt** (scene graph), har bir tugun (node) — obyekt, uning transform'i (joylashuv, aylanish, o'lcham) va bola-obyektlari bor:

```javascript
{
  world: {
    id: "world_1",
    terrain: {
      heightmap: "terrain_heightmap.png",  // balandlik xaritasi
      size: { width: 1000, depth: 1000 },
      textureLayers: [
        { texture: "grass.jpg", heightRange: [0, 50] },
        { texture: "rock.jpg", heightRange: [50, 200] },
        { texture: "snow.jpg", heightRange: [200, 500] }
      ]
    },
    entities: [
      {
        id: "entity_1",
        name: "Old Oak Tree",
        type: "mesh",
        modelAsset: "assets/tree_oak.glb",
        transform: {
          position: { x: 120, y: 0, z: 45 },
          rotation: { x: 0, y: 0.5, z: 0 },
          scale: { x: 1, y: 1.2, z: 1 }
        },
        components: [
          { type: "collider", shape: "capsule", radius: 0.5, height: 4 },
          { type: "lodGroup", levels: [ {distance: 50, mesh: "tree_high.glb"}, {distance: 200, mesh: "tree_low.glb"} ] }
        ],
        children: []  // masalan, daraxtga osilgan meva obyektlari
      }
    ],
    lighting: {
      sun: { direction: [0.5, -1, 0.3], intensity: 1.2, color: "#fff4e0" },
      ambient: { intensity: 0.3, color: "#404060" },
      fog: { density: 0.01, color: "#c8d8e8" }
    },
    skybox: "assets/sky_hdri.hdr"
  }
}
```

Bu tuzilma — Unity'ning Scene fayli yoki Godot'ning Scene Tree'siga juda o'xshash. DevForge kontekstida bu JSON to'g'ridan-to'g'ri Aurenis loyihangdagi world-building konsepsiyalar (world states, races, ecology) bilan integratsiya qilinishi mumkin.

---

## 3. Frontend: 3D Viewport (Three.js asosida)

### 3.1. Rendering Engine tanlash

| Kutubxona | Nima uchun yaxshi | Cheklovi |
|---|---|---|
| **Three.js** | Eng katta community, ko'p tayyor komponent (loader, controls, post-processing) | WebGL asosida (WebGPU'ga sekin o'tmoqda) |
| **Babylon.js** | Editor-ready funksiyalar ko'proq (built-in inspector, physics) | Bundle hajmi kattaroq |
| **PlayCanvas Engine** | To'liq editor tizimi bilan keladi (agar noldan yozmoqchi bo'lmasang) | Kamroq moslashuvchan, o'z formatiga bog'liq |

**Tavsiya:** **Three.js** — eng ko'p resurs, tutorial va DevForge kabi custom platformalar uchun eng moslashuvchan.

### 3.2. Viewport asosiy komponentlari

```javascript
// Asosiy viewport tuzilishi
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 5000);
const renderer = new THREE.WebGLRenderer({ antialias: true });

// Editor camera controls — Unity-style orbit/fly camera
const controls = new OrbitControls(camera, renderer.domElement);

// Transform Gizmo (move/rotate/scale handle)
const transformControls = new TransformControls(camera, renderer.domElement);
transformControls.attach(selectedObject);
scene.add(transformControls);

// Grid va gizmo'lar (faqat editor uchun, o'yinda ko'rinmaydi)
const gridHelper = new THREE.GridHelper(1000, 100);
scene.add(gridHelper);
```

### 3.3. Terrain (Relyef) tizimi

Terrain — heightmap (balandlik xaritasi, kulrang rasm) asosida generatsiya qilingan mesh:

```javascript
function generateTerrainMesh(heightmapImage, size) {
  const geometry = new THREE.PlaneGeometry(size.width, size.depth, 256, 256);
  const heightData = readPixelsFromImage(heightmapImage); // grayscale qiymatlar

  geometry.attributes.position.array.forEach((_, i) => {
    if (i % 3 === 2) { // Z (balandlik) komponenti
      const vertexIndex = Math.floor(i / 3);
      geometry.attributes.position.array[i] = heightData[vertexIndex] * maxHeight;
    }
  });
  geometry.computeVertexNormals();
  return new THREE.Mesh(geometry, terrainMaterial);
}
```

**Terrain sculpting** (relyefni "chizish" — tepalik, chuqurlik yaratish) — brush radius ichidagi vertex'larning Y (yoki Z) qiymatini o'zgartirish orqali amalga oshiriladi, real-time'da GPU vertex shader orqali eng tez ishlaydi.

### 3.4. Asset joylashtirish (Placement) tizimi

| Funksiya | Ishlash prinsipi |
|---|---|
| **Drag & drop** | Asset panelidan 3D viewport'ga sudrab tashlash → ray-casting orqali sichqoncha ostidagi terrain nuqtasi topiladi → obyekt o'sha joyga joylashtiriladi |
| **Gizmo (Move/Rotate/Scale)** | `TransformControls` — tanlangan obyektni sichqoncha bilan siljitish/aylantirish/kattalashtirish |
| **Snapping** | Grid'ga yoki boshqa obyektlarga "yopishish" (masalan har 1 metrda) |
| **Multi-select** | Bir nechta obyektni tanlab, birgalikda transform qilish |
| **Instancing (ko'plab nusxalash)** | O'rmon, o't kabi minglab bir xil obyektlarni GPU instancing orqali samarali render qilish (`InstancedMesh`) |
| **Prefab/Group** | Bir nechta obyektni birlashtirib, qayta ishlatiladigan shablon yaratish |

### 3.5. Katta dunyolar uchun performance: LOD va Frustum Culling

```javascript
// LOD (Level of Detail) — uzoqdagi obyektlar soddaroq mesh bilan ko'rsatiladi
const lod = new THREE.LOD();
lod.addLevel(highDetailMesh, 0);    // 0-50 metr
lod.addLevel(midDetailMesh, 50);    // 50-200 metr
lod.addLevel(lowDetailMesh, 200);   // 200+ metr

// Frustum culling — Three.js buni avtomatik qiladi,
// lekin katta dunyolarda qo'shimcha "chunk"larga bo'lish kerak:
// dunyo 100x100m bo'laklarga bo'linadi, faqat kamera ko'radigan
// chunk'lar yuklanadi (spatial partitioning / octree)
```

Ochiq dunyo (open-world) loyihalar uchun (Aurenis kabi) bu **eng muhim optimallashtirish** — butun xaritani bir vaqtda GPU'ga yuklash imkonsiz, shuning uchun **chunk-based streaming** kerak: foydalanuvchi kamera joylashuviga qarab faqat yaqin chunk'lar yuklanadi/render qilinadi, uzoqdagilari xotiradan tushiriladi.

---

## 4. Backend (Django): Asset Pipeline va Saqlash

### 4.1. 3D Model Import va Optimallashtirish

Foydalanuvchi yuklagan `.fbx`, `.obj`, `.blend` fayllar veb uchun mos formatga (`.glb`/`.gltf` — web-standard) konvertatsiya qilinishi va optimallashtirilishi kerak:

```python
# services/asset_pipeline.py
import subprocess

class AssetProcessor:
    def convert_to_gltf(self, input_path, output_path):
        """Blender headless orqali .blend/.fbx faylni .glb ga export qilish"""
        subprocess.run([
            "blender", "--background", "--python", "scripts/export_gltf.py",
            "--", input_path, output_path
        ])

    def optimize_mesh(self, glb_path):
        """gltf-transform yoki draco compression orqali fayl hajmini kamaytirish"""
        subprocess.run([
            "gltf-transform", "optimize", glb_path, glb_path.replace(".glb", "_opt.glb"),
            "--compress", "draco"
        ])

    def generate_lod_levels(self, glb_path):
        """Yuqori-poly modeldan avtomatik past-poly versiyalar yaratish"""
        # meshoptimizer yoki Blender decimate modifier orqali
        pass
```

**Blender headless mode** — Sardor allaqachon Blender bilan ishlagani uchun bu qism juda mos keladi: server'da Blender CLI orqali avtomatik model konversiya/optimallashtirish pipeline qurish mumkin.

### 4.2. World State saqlash

```python
# models.py
class World(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    scene_data = models.JSONField()  # to'liq scene graph
    heightmap = models.ImageField(upload_to='terrains/', null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/')

class WorldAsset(models.Model):
    world = models.ForeignKey(World, related_name='assets', on_delete=models.CASCADE)
    model_file = models.FileField(upload_to='models/')  # .glb
    original_file = models.FileField(upload_to='models_raw/')  # original .fbx/.blend
    asset_type = models.CharField(max_length=50)  # tree, rock, building, character...
    lod_levels = models.JSONField(default=list)
```

### 4.3. Export — boshqa engine'larga chiqarish

World Builder'da yaratilgan dunyoni Unity yoki Godot'ga eksport qilish (Sardor Unity bilan ishlagani uchun foydali funksiya):

```python
@shared_task
def export_world_to_unity(world_id):
    world = World.objects.get(id=world_id)
    # Scene JSON'ni Unity Scene formatiga (.unity YAML) yoki
    # oddiyroq — Unity'da parse qilinadigan custom JSON + asset package'ga aylantirish
    exporter = UnityWorldExporter(world.scene_data)
    package_path = exporter.build_unity_package(world.assets.all())
    return package_path
```

---

## 5. Fizik va o'yin-mexanika elementlari (ixtiyoriy, kengaytirilgan)

Agar World Builder faqat statik dunyo emas, balki **gameplay preview** ham bermoqchi bo'lsa (masalan Aurenis mexanikalarini sinab ko'rish uchun):

| Komponent | Kutubxona |
|---|---|
| **Physics (gravity, collision)** | Rapier.js (WebAssembly, tez) yoki Cannon-es |
| **Character controller** | Custom, capsule collider + raycast asosida |
| **Water/Ocean simulation** | Three.js Water shader yoki custom GPU shader |
| **Weather/particle system** | Three.js `Points` + custom shader (yomg'ir, qor, tuman) |
| **Day/Night cycle** | Sun direction'ni vaqt bo'yicha animatsiya qilish (lighting avtomatik yangilanadi) |

---

## 6. Ma'lumot oqimi (Data Flow)

```
1. Foydalanuvchi 3D model yuklaydi (.fbx/.obj/.blend) yoki tayyor asset tanlaydi
        │
        ▼
2. Celery: Blender headless orqali .glb ga konvertatsiya, optimallashtirish, LOD generatsiya
        │
        ▼
3. Frontend: Asset panelida ko'rinadi, drag & drop orqali 3D viewport'ga joylashtiriladi
        │
        ▼
4. Foydalanuvchi terrain sculpting, obyekt transform, yorug'lik sozlamalari bilan ishlaydi
   → Barchasi client-side, WebGL orqali real-time render qilinadi
   → Scene graph state doimiy yangilanadi
        │
        ▼
5. Auto-save: scene_data JSON Django'ga yuboriladi (asset fayllar emas, faqat metadata/reference)
        │
        ▼
6. "Export" bosilganda: to'liq scene + asset'lar serverga yuboriladi
   → Celery task → Unity/Godot formatiga yoki standalone .glb sahna sifatida export
   → Tayyor bo'lgach yuklab olish link'i beriladi
```

---

## 7. Tavsiya etilgan texnologik stack

```
Frontend:
  - Three.js — 3D rendering, scene graph
  - TransformControls, OrbitControls (Three.js addons) — editor navigatsiya
  - Rapier.js (WASM) — fizika simulyatsiyasi (ixtiyoriy)
  - React + react-three-fiber — agar React bilan integratsiya kerak bo'lsa

Backend (Django, mavjud stackingga mos):
  - Blender (headless/CLI) — model konversiya, optimallashtirish
  - gltf-transform / Draco — GLB fayl siqish
  - Celery + Redis — asset processing queue
  - django-storages + S3/CDN — katta 3D model fayllarni saqlash/uzatish
  - Django Channels — real-time hamkorlik (bir nechta odam bitta dunyoda)

Ixtiyoriy AI qo'shimchalar:
  - Procedural terrain generation (Perlin/Simplex noise asosida avtomatik relyef)
  - AI texture generation (Stable Diffusion — terrain texture'lar uchun)
  - Auto-LOD generation (meshoptimizer)
```

---

## 8. Bosqichma-bosqich rivojlantirish rejasi

**1-bosqich (MVP):**
- 3D viewport (Three.js), kamera boshqaruvi (orbit)
- Oddiy obyekt joylashtirish (drag & drop, gizmo bilan move/rotate/scale)
- Scene save/load (JSON)

**2-bosqich:**
- Terrain sistema (heightmap asosida relyef, texture layerlar)
- Asset pipeline (Blender orqali model import/optimize)
- Lighting sozlamalari (sun, ambient, fog)

**3-bosqich:**
- Terrain sculpting brush
- Instancing (o'rmon, o'tloq kabi ko'plab obyektlar)
- LOD tizimi, chunk-based streaming (katta dunyolar uchun)

**4-bosqich (professional):**
- Fizika simulyatsiyasi, gameplay preview
- Unity/Godot export
- Real-time hamkorlik (bir nechta foydalanuvchi bitta dunyoda ishlashi)
- AI-powered procedural generation (terrain, texture)

---

## 9. Xulosa

World Builder — boshqa uchta modul (Image, Video, Audio) dan farqli o'laroq, **to'liq client-side GPU rendering** (WebGL/Three.js) ga tayanadi, server esa faqat **asset optimallashtirish (Blender pipeline) va saqlash/export** vazifasini bajaradi. Bu modul texnik jihatdan eng murakkab, lekin Sardorning Blender va Unity tajribasi tufayli asset pipeline qismini qurish uchun mavjud bilim bazasi allaqachon bor. Katta dunyolar bilan ishlashda **LOD va chunk-based streaming** — performance uchun eng muhim arxitektura qarori bo'lib qoladi.

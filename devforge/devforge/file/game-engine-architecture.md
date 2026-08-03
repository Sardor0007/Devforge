# Web-based Game Engine — To'liq Arxitektura Hujjati

> DevForge Studio Editor moduli uchun — Django 5 backend + JS/WebGL frontend
> World Builder'ning "davomi" — u yaratgan dunyoni haqiqiy o'ynaladigan o'yinga aylantiruvchi qatlam

---

## 1. Umumiy Arxitektura va Game Engine bilan World Builder farqi

World Builder — **statik sahna muharriri** (obyektlarni joylashtirish, terrain, yorug'lik). Game Engine esa shu sahnani **jonli, interaktiv, mantiq bilan boshqariladigan** tizimga aylantiradi: skriptlar, fizika, animatsiya, input, va yakunda — **build qilib chiqarish** (brauzer, desktop, mobil uchun export).

```
┌─────────────────────────────────────────────────────────────┐
│                     BROWSER (Editor + Runtime)                │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌──────────────┐  │
│  │ ECS Core   │ │ Render    │ │ Physics    │ │ Script/Node   │  │
│  │ (Entity-   │ │ Pipeline  │ │ Engine     │ │ Editor        │  │
│  │ Component- │ │ (Three.js/│ │ (Rapier/   │ │ (visual/     │  │
│  │ System)    │ │  WebGPU)  │ │  Cannon)   │ │  JS/Python)   │  │
│  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └──────┬────────┘  │
│        └──────────────┴──────────────┴─────────────┘          │
│                    Game Loop (Update/Render Cycle)             │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  Input System │ Audio System │ Animation System │ UI    │    │
│  └───────────────────────────────────────────────────────┘    │
└────────────────────────┬──────────────────────────────────── ┘
                          │ REST/WebSocket
┌─────────────────────────▼───────────────────────────────┐
│                  DJANGO BACKEND (Server)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Project/Asset │  │ Build Pipeline│  │ Multiplayer     │ │
│  │ Storage       │  │ (export to    │  │ Server (netcode,│ │
│  │ (versioning)  │  │  web/desktop) │  │  authoritative) │ │
│  └──────────────┘  └──────────────┘  └────────────────┘ │
└───────────────────────────────────────────────────────── ┘
```

**Muhim tushuncha:** Game Engine — bu ikkita rejimda ishlaydigan bitta kod bazasi: **Editor rejimi** (Sardor sahnani tuzadi, skript yozadi, sinab ko'radi) va **Runtime rejimi** (yakuniy o'yinchi shu kodni o'ynaydi, editor UI'siz). Professional enginelar (Unity, Godot, Unreal) barchasi shu prinsipga amal qiladi.

---

## 2. ECS (Entity-Component-System) — Engine'ning yuragi

Zamonaviy o'yin dvigatellari OOP (klass-based inheritance) o'rniga **ECS arxitekturasi**ni ishlatadi — bu moslashuvchanroq va tezroq:

- **Entity** — shunchaki ID (masalan `entity_42`), o'zida hech qanday logika yo'q
- **Component** — faqat ma'lumot (masalan `Position{x,y,z}`, `Health{current,max}`, `Sprite{texture}`)
- **System** — logikani bajaradi, ma'lum component kombinatsiyasiga ega barcha entity'larni qayta ishlaydi

```javascript
// Component'lar — faqat ma'lumot
class Position { constructor(x, y, z) { this.x = x; this.y = y; this.z = z; } }
class Velocity { constructor(dx, dy, dz) { this.dx = dx; this.dy = dy; this.dz = dz; } }
class Health   { constructor(current, max) { this.current = current; this.max = max; } }

// System — logika
class MovementSystem {
  update(world, deltaTime) {
    // Position VA Velocity component'iga ega barcha entity'larni topish
    const entities = world.query([Position, Velocity]);
    for (const entity of entities) {
      const pos = entity.get(Position);
      const vel = entity.get(Velocity);
      pos.x += vel.dx * deltaTime;
      pos.y += vel.dy * deltaTime;
      pos.z += vel.dz * deltaTime;
    }
  }
}
```

**Nega ECS?** Chunki o'yin obyektlari juda xilma-xil xatti-harakatga ega bo'lishi mumkin (uchuvchi dushman, statik xazina qutisi, o'ynovchi belgi) — klass-based inheritance'da bu "Dushman extends Uchuvchi extends Xarakter..." kabi chalkash ierarxiyalarga olib keladi. ECS'da esa xohlagan component kombinatsiyasini qo'shib, xohlagan xatti-harakatni yig'ish mumkin (composition over inheritance).

Tayyor JS ECS kutubxonalari: **bitECS** (juda tez, WASM-friendly), **ecsy**, yoki **miniplex** (soddaroq loyihalar uchun).

---

## 3. Game Loop — Har freym nima sodir bo'ladi

```javascript
function gameLoop(currentTime) {
  const deltaTime = (currentTime - lastTime) / 1000;

  // 1. Input yig'ish
  inputSystem.poll();

  // 2. Fixed timestep physics (deterministik bo'lishi uchun)
  accumulator += deltaTime;
  while (accumulator >= FIXED_TIMESTEP) {
    physicsSystem.step(FIXED_TIMESTEP);
    accumulator -= FIXED_TIMESTEP;
  }

  // 3. Gameplay logika (skriptlar, AI, animatsiya)
  scriptSystem.update(deltaTime);
  animationSystem.update(deltaTime);
  audioSystem.update(deltaTime);

  // 4. Render (interpolatsiya bilan, silliqlik uchun)
  const alpha = accumulator / FIXED_TIMESTEP;
  renderSystem.render(alpha);

  requestAnimationFrame(gameLoop);
}
```

**Muhim arxitektura qarori:** Fizika **fixed timestep** (masalan 60Hz) bilan, render esa **variable timestep** (brauzer FPS'iga qarab) bilan ishlashi kerak — aks holda turli tezlikdagi kompyuterlarda o'yin xatti-harakati farq qiladi (masalan sakrash balandligi FPS'ga bog'liq bo'lib qoladi).

---

## 4. Render Pipeline

World Builder'dan meros bo'lib qolgan Three.js asosidagi rendering, lekin qo'shimcha runtime kerakli qatlamlar bilan:

| Qatlam | Vazifasi |
|---|---|
| **Camera system** | 3rd person, 1st person, top-down — kamera turlari, smooth follow |
| **Material/Shader system** | PBR (Physically Based Rendering) materiallar, custom shader'lar |
| **Post-processing** | Bloom, SSAO, color grading, motion blur (Three.js `EffectComposer` orqali) |
| **Particle system** | GPU-based particle'lar (portlash, tutun, sehr effektlari) |
| **Sprite/2D rendering** | Agar 2D o'yinlar ham qo'llab-quvvatlansa — alohida ortho camera pipeline |
| **UI overlay** | HUD, menyu — HTML/CSS overlay yoki in-canvas UI (masalan `three-mesh-ui`) |

---

## 5. Physics Engine

| Kutubxona | Xususiyat |
|---|---|
| **Rapier.js** (WASM, Rust asosida) | Eng tez, deterministik, ko'p platformali (server-side'da ham xuddi shu natija — multiplayer uchun muhim) |
| **Cannon-es** | Sof JavaScript, o'rnatish osonroq, lekin sekinroq |
| **Ammo.js** (Bullet Physics port) | Kuchli, lekin murakkabroq API |

**Tavsiya:** **Rapier.js** — chunki WASM orqali ishlaydi (native tezlikka yaqin) va **deterministik** (bir xil input bilan har doim bir xil natija beradi) — bu ayniqsa multiplayer (server va client bir xil fizik natijaga kelishi kerak bo'lganda) uchun kritik.

```javascript
import RAPIER from '@dimforge/rapier3d';

const world = new RAPIER.World({ x: 0, y: -9.81, z: 0 });
const rigidBody = world.createRigidBody(RAPIER.RigidBodyDesc.dynamic());
const collider = world.createCollider(RAPIER.ColliderDesc.capsule(0.5, 0.3), rigidBody);

// Har fixed timestep'da
world.step();
```

---

## 6. Scripting System — Foydalanuvchi mantiq yozadigan joy

Bu — engine'ning eng muhim qismi, chunki bu yerda foydalanuvchi (yoki Sardor Aurenis kabi loyihalar uchun) o'z o'yin mantig'ini yozadi. Ikki yondashuv mumkin, ular birga ham ishlashi mumkin:

### 6.1. Visual Scripting (Node-based) — dasturchi bo'lmaganlar uchun

Blueprint (Unreal) yoki Godot Visual Script'ga o'xshash — node'larni chizib mantiq yaratish:

```javascript
{
  graph: {
    nodes: [
      { id: "n1", type: "event/onCollision", outputs: ["exec"] },
      { id: "n2", type: "action/playSound", inputs: ["exec"], params: { sound: "explosion.wav" } },
      { id: "n3", type: "action/destroyEntity", inputs: ["exec"] }
    ],
    connections: [
      { from: "n1.exec", to: "n2.exec" },
      { from: "n2.exec", to: "n3.exec" }
    ]
  }
}
```

Bu graph runtime'da kichik bir "interpreter" orqali bajariladi — har node o'zining `execute()` funksiyasiga ega, va `exec` bog'lanish orqali keyingi node'ga signal uzatiladi. Frontend'da buni chizish uchun **Rete.js** yoki **LiteGraph.js** kabi tayyor node-editor kutubxonalari bor.

### 6.2. Kod-based Scripting — dasturchilar uchun (Sardorga mos)

```javascript
// Entity'ga biriktiriladigan skript komponenti
class EnemyAI extends ScriptComponent {
  onStart() {
    this.speed = 3.0;
    this.target = this.world.findEntityByTag("player");
  }

  onUpdate(deltaTime) {
    const direction = this.target.position.clone().sub(this.entity.position).normalize();
    this.entity.position.addScaledVector(direction, this.speed * deltaTime);
  }

  onCollision(other) {
    if (other.hasTag("player")) {
      other.getComponent(Health).damage(10);
    }
  }
}
```

Bu yondashuv **sandboxda** ishlashi kerak — foydalanuvchi kodini to'g'ridan-to'g'ri main thread'da ishlatish xavfsizlik muammosi (agar boshqa foydalanuvchilar loyihalarni ko'rishi/ijro etishi mumkin bo'lsa). Yechim:
- **Web Worker + iframe sandbox** orqali skriptni izolyatsiya qilish
- Yoki **QuickJS-WASM** kabi to'liq sandboxed JS interpreter ishlatish (server-side kodni tahlil qilib zararli funksiyalarni bloklash bilan birga)

Sardor Python bilan ko'p ishlagani uchun, muqobil variant: **Pyodide** (WASM orqali Python brauzerda) — foydalanuvchilar Python skript yozib, brauzerda ishlatilishi mumkin (garchi bu JS'dan sekinroq bo'lsa ham, prototiplashtirish uchun qulay).

---

## 7. Asset va Sahna integratsiyasi (World Builder bilan bog'lanish)

Game Engine World Builder'da yaratilgan `scene_data` (JSON) ni **to'g'ridan-to'g'ri** yuklab, ustiga runtime component'lar (fizika, skript, AI) qo'shadi:

```javascript
function loadSceneIntoRuntime(worldSceneData) {
  const ecsWorld = new ECSWorld();

  worldSceneData.entities.forEach(entityData => {
    const entity = ecsWorld.createEntity();
    entity.addComponent(new Transform(entityData.transform));
    entity.addComponent(new MeshRenderer(entityData.modelAsset));

    // World Builder'dagi statik "collider" component'i endi jonli physics body'ga aylanadi
    const colliderData = entityData.components.find(c => c.type === "collider");
    if (colliderData) {
      entity.addComponent(new RigidBody(colliderData));
    }

    // Agar entity'ga skript biriktirilgan bo'lsa
    if (entityData.script) {
      entity.addComponent(new ScriptComponent(entityData.script));
    }
  });

  return ecsWorld;
}
```

Bu — DevForge arxitekturasining eng kuchli tomoni bo'ladi: **World Builder — dizayn vaqti (design-time), Game Engine — ijro vaqti (runtime)**. Ikkalasi bir xil ma'lumot formatini ishlatadi, shuning uchun World Builder'da qurilgan har qanday sahna to'g'ridan-to'g'ri "Play" tugmasi bilan jonlantiriladi.

---

## 8. Backend (Django): Loyiha, Build va Multiplayer

### 8.1. Loyiha va versiyalash

```python
# models.py
class GameProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    world = models.ForeignKey('World', on_delete=models.CASCADE)  # World Builder bilan bog'liq
    scripts = models.JSONField(default=dict)  # entity_id -> script code/graph
    game_settings = models.JSONField(default=dict)  # gravity, input mapping, va h.k.
    version = models.IntegerField(default=1)

class GameBuild(models.Model):
    project = models.ForeignKey(GameProject, related_name='builds', on_delete=models.CASCADE)
    target = models.CharField(max_length=50)  # 'web', 'desktop', 'android'
    status = models.CharField(max_length=20, default='pending')
    output_file = models.FileField(upload_to='builds/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 8.2. Build Pipeline — "Export" tugmasi bosilganda

```python
@shared_task(bind=True)
def build_game(self, project_id, target="web"):
    project = GameProject.objects.get(id=project_id)
    build = GameBuild.objects.create(project=project, target=target, status="building")

    if target == "web":
        # Barcha asset, skript, sahna ma'lumotini bitta bundle'ga yig'ish
        bundle = build_web_bundle(project)  # webpack/esbuild orqali JS bundle
        output_path = f"builds/{project_id}_web.zip"
        package_web_build(bundle, project.world.assets.all(), output_path)

    elif target == "desktop":
        # Electron yoki Tauri orqali standalone desktop app yaratish
        output_path = build_desktop_package(project)

    build.output_file = output_path
    build.status = "completed"
    build.save()
    notify_build_complete(build.id)
```

Web build uchun **esbuild** yoki **Vite** orqali barcha runtime kod + foydalanuvchi skriptlari + asset'lar bitta optimallashtirilgan bundle'ga yig'iladi (production'da tez yuklanishi uchun minifikatsiya, tree-shaking bilan).

### 8.3. Multiplayer (ixtiyoriy, kengaytirilgan bosqich)

Agar o'yin multiplayer bo'lsa, **authoritative server** modeli tavsiya etiladi (cheat'lardan himoya uchun):

```python
# Django Channels orqali game server
class GameSessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        await self.channel_layer.group_add(f"game_{self.room_id}", self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        input_data = json.loads(text_data)
        # Server o'zining fizika world'ida (Rapier - Python binding yoki Node.js
        # microservice orqali) inputni qayta ishlaydi va natijani hisoblaydi
        result = self.game_state.apply_input(self.scope['user'].id, input_data)

        # Yangi state barcha clientlarga tarqatiladi
        await self.channel_layer.group_send(f"game_{self.room_id}", {
            "type": "state_update", "data": result
        })
```

**Muhim eslatma:** Django/Python real-time fizika hisoblash uchun ideal emas (GIL, sekinlik). Katta multiplayer loyihalar uchun alohida **Node.js yoki Rust game server microservice** qurish, Django esa faqat autentifikatsiya/matchmaking/loyiha boshqaruvi uchun qolishi tavsiya etiladi.

---

## 9. Ma'lumot oqimi (Data Flow)

```
1. World Builder'da sahna yaratiladi (statik: terrain, obyektlar, yorug'lik)
        │
        ▼
2. Game Engine shu sahnani yuklaydi, ECS world'ga aylantiradi
   → Har entity'ga component qo'shiladi (Transform, MeshRenderer, RigidBody...)
        │
        ▼
3. Foydalanuvchi skript yozadi/biriktiradi (kod yoki visual node graph)
        │
        ▼
4. "Play" tugmasi — Editor rejimidan Runtime rejimiga o'tadi
   → Game Loop ishga tushadi: Input → Physics → Script → Render, har freym
        │
        ▼
5. Auto-save: scripts, game_settings Django'ga yuboriladi
        │
        ▼
6. "Export/Build" bosilganda: Celery task → barcha kod+asset bitta bundle'ga
   yig'iladi → tayyor build (ZIP/Electron app) yuklab olish uchun beriladi
        │
        ▼
7. (Ixtiyoriy) Multiplayer: WebSocket orqali server-authoritative state sync
```

---

## 10. Tavsiya etilgan texnologik stack

```
Frontend:
  - Three.js — rendering (World Builder bilan bir xil)
  - bitECS yoki miniplex — Entity-Component-System yadrosi
  - Rapier.js (WASM) — fizika, deterministik
  - Rete.js / LiteGraph.js — visual scripting editor (ixtiyoriy)
  - Pyodide (ixtiyoriy) — Python skriptlash imkoniyati brauzerda

Backend (Django, mavjud stackingga mos):
  - Celery + Redis — build pipeline, asset processing
  - esbuild/Vite (Node subprocess orqali) — production bundle yaratish
  - Electron/Tauri — desktop build uchun (ixtiyoriy)
  - Django Channels — multiplayer state sync (kichik loyihalar uchun yetarli)
  - django-storages + S3/CDN — build fayllarni saqlash/tarqatish

Kattaroq multiplayer uchun (ixtiyoriy, keyingi bosqich):
  - Node.js/Rust alohida game-server microservice (authoritative physics)
  - Redis Pub/Sub — Django va game-server orasida kommunikatsiya
```

---

## 11. Bosqichma-bosqich rivojlantirish rejasi

**1-bosqich (MVP):**
- World Builder sahnasini yuklab, statik "Play mode" preview (fizikasiz, skriptsiz)
- Oddiy input tizimi (klaviatura/sichqoncha)
- Asosiy ECS: Transform, MeshRenderer component'lari

**2-bosqich:**
- Rapier.js integratsiyasi — asosiy fizika (gravity, collision)
- Kod-based scripting (JS, sandboxed Web Worker orqali)
- Basic kamera tizimi (3rd person/1st person)

**3-bosqich:**
- Visual scripting (node-based, dasturchi bo'lmaganlar uchun)
- Animatsiya tizimi, audio integratsiyasi (Audio Lab bilan bog'lanish)
- Web build/export pipeline

**4-bosqich (professional):**
- Multiplayer (authoritative server, netcode)
- Desktop/mobil build (Electron/Tauri)
- Advanced rendering (post-processing, PBR materiallar)
- Visual scripting + kod scripting'ni birlashtirish (hybrid tizim)

---

## 12. Xulosa

Game Engine — DevForge'dagi to'rtta studio modulini (Image, Video, Audio, World Builder) **bitta yashovchi mahsulotga** bog'laydigan yakuniy qatlam: World Builder'da qurilgan dunyo, Audio Lab'da tayyorlangan ovozlar, va foydalanuvchi yozgan skriptlar — hammasi shu Game Loop ichida birlashadi. Arxitektura jihatidan eng muhim qarorlar: **ECS** (moslashuvchan gameplay mantig'i uchun), **fixed-timestep physics** (deterministik xatti-harakat uchun), va **sandboxed scripting** (xavfsizlik uchun, ayniqsa DevForge ko'p foydalanuvchili platforma bo'lgani sabab). Aurenis kabi loyihalar uchun bu engine — g'oyani prototipdan o'ynaladigan demogacha olib chiqishning to'g'ridan-to'g'ri yo'li bo'ladi.

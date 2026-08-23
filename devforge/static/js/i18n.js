/**
 * ═════════════════════════════════════════════════════════════════
 *  DEVFORGE MULTI-LANGUAGE (i18n) ENGINE
 *  Supported Languages:
 *    - 'uz': O'zbekcha 🇺🇿
 *    - 'ru': Русский   🇷🇺
 *    - 'en': English   🇬🇧
 * ═════════════════════════════════════════════════════════════════
 */

(function() {
  const TRANSLATIONS = {
    uz: {
      // Nav & Header
      "nav.tools": "Vositalar",
      "nav.features": "Imkoniyatlar",
      "nav.pricing": "Tariflar",
      "nav.faq": "Savol-Javob",
      "nav.community": "Hamjamiyat",
      "nav.login": "Kirish",
      "nav.register": "Qo'shilish",
      "nav.get_started": "Bepul boshlash",
      "nav.dashboard": "Boshqaruv paneli",
      "nav.projects": "Loyihalar",
      "nav.assets": "3D Assetlar",
      "nav.marketplace": "Marketplace",
      "nav.workspace": "Workspace",
      "nav.feed": "Lenta",
      "nav.jobs": "Vakansiyalar",
      "nav.learn": "O'rganish",
      "nav.challenges": "Chellenjlar",
      "nav.jams": "Game Jamlar",
      "nav.leaderboard": "Reyting",
      "nav.wallet": "Hamyon",
      "nav.subscription": "Obuna",
      "nav.logout": "Chiqish",
      "nav.my_profile": "Profilim",
      "nav.search_placeholder": "Qidirish...",

      // Landing Hero
      "hero.badge": "Hozirda Ochiq Beta — Minglab ijodkorlarga qo'shiling",
      "hero.title_start": "Yarating",
      "hero.title_mid": "Quring",
      "hero.title_end": "Nashr eting.",
      "hero.subtitle": "3D Studio, Game Engine, Photoshop-uslubli tahrirlagich, Audio DAW va barcha kreativ vositalar bitta platformada. Brauzerdan chiqmasdan eng ajoyib o'yinlarni quring.",
      "hero.cta_free": "⚡ Bepul boshlash — Karta talab etilmaydi",
      "hero.cta_browse": "🎮 Loyihalarni ko'rish →",
      "hero.stats_creators": "Faol Ijodkorlar",
      "hero.stats_projects": "Chiqarilgan Loyihalar",
      "hero.stats_assets": "Mavjud 3D Assetlar",
      "hero.stats_tools": "Kreativ Vositalar",

      // Tools Showcase
      "tools.eyebrow": "Sizga Kerak Bo'lgan Hamma Narsa",
      "tools.title": "To'liq Kreativ Dasturlar To'plami, To'g'ridan-to'g'ri Brauzeringizda",
      "tools.subtitle": "Yuklab olish yoki o'rnatish shart emas. Faqat brauzerni oching va ijodni boshlang.",
      "tools.studio_3d": "3D Studio Pro",
      "tools.studio_3d_desc": "Three.js asosidagi professional 3D muhit. Blender-uslubidagi asboblar bilan modellar yarating, haykaltaroshlik qiling va animatsiya bering. GLTF, OBJ yoki 4K formatda eksport qiling.",
      "tools.game_engine": "Game Engine (O'yin Dvigateli)",
      "tools.game_engine_desc": "2D va 3D o'yinlarni vizual muharrir, fizika dvigateli va skriptlar bilan yarating. Web, Android va iOS ga bitta klikda eksport qiling.",
      "tools.image_editor": "Image Editor (Grafik Tahrirlovchi)",
      "tools.image_editor_desc": "Photoshop-uslubidagi qatlamli (layer-based) rasm muharriri. Cho'tkalar, filtrlar, maskalar va effektlar.",
      "tools.audio_lab": "Audio Lab (DAW)",
      "tools.audio_lab_desc": "Ko'p yo'lli audio sekvenser, virtual cholg'ular va bit-mashina. O'yinlar uchun saundtreklarni professional yarating.",
      "tools.video_lab": "Video Lab",
      "tools.video_lab_desc": "Vaqt o'qiga ega video muharrir. Kesish, musiqalar, o'tishlar va 4K gacha eksport.",
      "tools.world_builder": "World Builder (Dunyo Yaratuvchi)",
      "tools.world_builder_desc": "3D o'yin xaritalari, relyef va tabiiy muhitlarni protsedurali yaratish.",
      "tools.marketplace_card": "Asset Marketplace",
      "tools.marketplace_desc": "Yuqori sifatli 3D modellar, teksturalar va musiqalarni sotib oling yoki soting. Birinchi kundan daromad qiling.",
      "tools.jams_card": "Game Jamlar va Chellenjlar",
      "tools.jams_desc": "Sovrinli Game Jamlarda qatnashing, jamoalar tuzing va reytingda yuqorilang.",

      // Pricing
      "pricing.eyebrow": "Oddiy va Aniq Narxlar",
      "pricing.title": "Bepul boshlang. Tayyor bo'lganda kengaytiring.",
      "pricing.subtitle": "Yashirin to'lovlarsiz. Istalgan vaqtda tarifni o'zgartiring yoki bekor qiling.",
      "pricing.monthly": "Oylik",
      "pricing.yearly": "Yillik",
      "pricing.save_30": "30% Tejang",
      "pricing.free_name": "Free (Bepul)",
      "pricing.pro_name": "Pro",
      "pricing.studio_name": "Studio",
      "pricing.enterprise_name": "Enterprise",
      "pricing.free_cta": "Bepul Boshlash",
      "pricing.pro_cta": "Pro Rejani Tanlash →",
      "pricing.studio_cta": "Studio Rejani Tanlash →",
      "pricing.enterprise_cta": "Bog'lanish →",

      // 3D Studio
      "studio.file": "Fayl",
      "studio.edit": "Tahrirlash",
      "studio.add": "Qo'shish",
      "studio.object": "Ob'ekt",
      "studio.view": "Ko'rinish",
      "studio.render": "Render",
      "studio.save": "Saqlash",
      "studio.saved": "Saqlangan",
      "studio.saving": "Saqlanmoqda...",
      "studio.outliner": "Outliner (Ob'ektlar ro'yxati)",
      "studio.properties": "Xususiyatlar",
      "studio.materials": "Materiallar",
      "studio.modifiers": "Modifikatorlar",
      "studio.timeline": "Vaqt O'qi (Timeline)",
      "studio.frame": "Freym",

      // Common
      "common.language": "Til",
      "common.loading": "Yuklanmoqda...",
      "common.cancel": "Bekor qilish",
      "common.confirm": "Tasdiqlash",
      "common.save_changes": "O'zgarishlarni saqlash",
      "common.delete": "O'chirish",
      "common.search": "Qidiruv"
    },

    ru: {
      // Nav & Header
      "nav.tools": "Инструменты",
      "nav.features": "Возможности",
      "nav.pricing": "Тарифы",
      "nav.faq": "Вопросы",
      "nav.community": "Сообщество",
      "nav.login": "Вход",
      "nav.register": "Регистрация",
      "nav.get_started": "Начать бесплатно",
      "nav.dashboard": "Панель управления",
      "nav.projects": "Проекты",
      "nav.assets": "3D Ассеты",
      "nav.marketplace": "Маркетплейс",
      "nav.workspace": "Воркспейс",
      "nav.feed": "Лента",
      "nav.jobs": "Вакансии",
      "nav.learn": "Обучение",
      "nav.challenges": "Челленджи",
      "nav.jams": "Game Jam",
      "nav.leaderboard": "Рейтинг",
      "nav.wallet": "Кошелек",
      "nav.subscription": "Подписка",
      "nav.logout": "Выйти",
      "nav.my_profile": "Мой профиль",
      "nav.search_placeholder": "Поиск...",

      // Landing Hero
      "hero.badge": "Открытая бета — Присоединяйтесь к тысячам создателей",
      "hero.title_start": "Создавайте",
      "hero.title_mid": "Стройте",
      "hero.title_end": "Публикуйте.",
      "hero.subtitle": "3D Studio, Game Engine, графический редактор, аудио DAW и все творческие инструменты на одной платформе. Создавайте игры прямо в браузере.",
      "hero.cta_free": "⚡ Начать бесплатно — Без карты",
      "hero.cta_browse": "🎮 Смотреть проекты →",
      "hero.stats_creators": "Активных авторов",
      "hero.stats_projects": "Опубликованных игр",
      "hero.stats_assets": "3D Ассетов",
      "hero.stats_tools": "Творческих студий",

      // Tools Showcase
      "tools.eyebrow": "Все необходимое для творчества",
      "tools.title": "Полный стек инструментов прямо в браузере",
      "tools.subtitle": "Никаких загрузок и установок. Откройте вкладку и начните создавать.",
      "tools.studio_3d": "3D Studio Pro",
      "tools.studio_3d_desc": "Профессиональная 3D среда на Three.js. Создавайте, моделируйте и анимируйте с инструментами в стиле Blender. Экспорт в GLTF, OBJ и рендер 4K.",
      "tools.game_engine": "Game Engine (Игровой движок)",
      "tools.game_engine_desc": "Создавайте 2D и 3D игры с визуальным редактором сцен, физикой и скриптами. Экспорт в Web, Android и iOS в один клик.",
      "tools.image_editor": "Image Editor (Графический редактор)",
      "tools.image_editor_desc": "Полноценный редактор в стиле Photoshop со слоями, кистями, масками, фильтрами и эффектами.",
      "tools.audio_lab": "Audio Lab (DAW)",
      "tools.audio_lab_desc": "Многодорожечный аудио секвенсор, виртуальные инструменты и драм-машина для написания игровых саундтреков.",
      "tools.video_lab": "Video Lab",
      "tools.video_lab_desc": "Таймлайн видеоредактор. Монтаж, переходы, наложение звука и экспорт до 4K.",
      "tools.world_builder": "World Builder (Конструктор миров)",
      "tools.world_builder_desc": "Процедурная генерация ландшафтов, 3D окружения и игровых миров.",
      "tools.marketplace_card": "Asset Marketplace",
      "tools.marketplace_desc": "Покупайте и продавайте 3D модели, текстуры и звуки. Монетизируйте творчество с первого дня.",
      "tools.jams_card": "Game Jam и Челленджи",
      "tools.jams_desc": "Участвуйте в соревнованиях с призовыми фондами, собирайте команды и побеждайте.",

      // Pricing
      "pricing.eyebrow": "Прозрачные тарифы",
      "pricing.title": "Начните бесплатно. Масштабируйте при росте.",
      "pricing.subtitle": "Без скрытых платежей. Изменяйте или отменяйте план в любой момент.",
      "pricing.monthly": "Ежемесячно",
      "pricing.yearly": "Ежегодно",
      "pricing.save_30": "Скидка 30%",
      "pricing.free_name": "Free (Бесплатный)",
      "pricing.pro_name": "Pro",
      "pricing.studio_name": "Studio",
      "pricing.enterprise_name": "Enterprise",
      "pricing.free_cta": "Начать бесплатно",
      "pricing.pro_cta": "Выбрать Pro план →",
      "pricing.studio_cta": "Выбрать Studio план →",
      "pricing.enterprise_cta": "Связаться с нами →",

      // 3D Studio
      "studio.file": "Файл",
      "studio.edit": "Правка",
      "studio.add": "Добавить",
      "studio.object": "Объект",
      "studio.view": "Вид",
      "studio.render": "Рендер",
      "studio.save": "Сохранить",
      "studio.saved": "Сохранено",
      "studio.saving": "Сохранение...",
      "studio.outliner": "Аутлайнер (Объекты)",
      "studio.properties": "Свойства",
      "studio.materials": "Материалы",
      "studio.modifiers": "Модификаторы",
      "studio.timeline": "Таймлайн",
      "studio.frame": "Кадр",

      // Common
      "common.language": "Язык",
      "common.loading": "Загрузка...",
      "common.cancel": "Отмена",
      "common.confirm": "Подтвердить",
      "common.save_changes": "Сохранить изменения",
      "common.delete": "Удалить",
      "common.search": "Поиск"
    },

    en: {
      // Nav & Header
      "nav.tools": "Tools",
      "nav.features": "Features",
      "nav.pricing": "Pricing",
      "nav.faq": "FAQ",
      "nav.community": "Community",
      "nav.login": "Log in",
      "nav.register": "Get Started",
      "nav.get_started": "Get Started Free",
      "nav.dashboard": "Dashboard",
      "nav.projects": "Projects",
      "nav.assets": "3D Assets",
      "nav.marketplace": "Marketplace",
      "nav.workspace": "Workspace",
      "nav.feed": "Feed",
      "nav.jobs": "Jobs",
      "nav.learn": "Learn",
      "nav.challenges": "Challenges",
      "nav.jams": "Game Jams",
      "nav.leaderboard": "Leaderboard",
      "nav.wallet": "Wallet",
      "nav.subscription": "Subscription",
      "nav.logout": "Log out",
      "nav.my_profile": "My Profile",
      "nav.search_placeholder": "Search anything...",

      // Landing Hero
      "hero.badge": "Now in Public Beta — Join thousands of creators",
      "hero.title_start": "Build",
      "hero.title_mid": "Create",
      "hero.title_end": "Publish.",
      "hero.subtitle": "The all-in-one creative platform with 3D Studio, Game Engine, Image Editor, Audio DAW, and more. Build the next great game — without leaving your browser.",
      "hero.cta_free": "⚡ Start for Free — No Card Required",
      "hero.cta_browse": "🎮 Browse Projects →",
      "hero.stats_creators": "Active Creators",
      "hero.stats_projects": "Projects Published",
      "hero.stats_assets": "3D Assets Available",
      "hero.stats_tools": "Creative Tools",

      // Tools Showcase
      "tools.eyebrow": "Everything You Need",
      "tools.title": "A Full Creative Suite, Right in Your Browser",
      "tools.subtitle": "No downloads. No plugins. Just open a tab and start creating.",
      "tools.studio_3d": "3D Studio Pro",
      "tools.studio_3d_desc": "A professional-grade 3D environment powered by Three.js. Create, sculpt, and animate 3D models with Blender-inspired tools. Export as GLTF, OBJ, or 4K renders.",
      "tools.game_engine": "Game Engine",
      "tools.game_engine_desc": "Build 2D and 3D games with a visual scene editor, physics engine, and scripting. One-click export to Web, Android, and iOS.",
      "tools.image_editor": "Image Editor",
      "tools.image_editor_desc": "Photoshop-like layer-based image editor. Brushes, masks, filters, blend modes, and non-destructive editing.",
      "tools.audio_lab": "Audio Lab (DAW)",
      "tools.audio_lab_desc": "Multi-track audio sequencer with virtual instruments, beat machine, and waveform editor. Compose soundtracks in-browser.",
      "tools.video_lab": "Video Lab",
      "tools.video_lab_desc": "Timeline-based video editor. Trim, splice, transitions, audio mixing, and export up to 4K.",
      "tools.world_builder": "World Builder",
      "tools.world_builder_desc": "Craft immersive 3D game worlds with terrain tools, foliage painting, and atmospheric lighting.",
      "tools.marketplace_card": "Asset Marketplace",
      "tools.marketplace_desc": "Buy and sell high-quality 3D models, textures, audio packs, and scripts. Monetize your creations from day one.",
      "tools.jams_card": "Game Jams & Challenges",
      "tools.jams_desc": "Host or join competitive Game Jams with prize pools, real-time leaderboards, and community voting.",

      // Pricing
      "pricing.eyebrow": "Simple Pricing",
      "pricing.title": "Start Free. Scale When Ready.",
      "pricing.subtitle": "No lock-ins, no surprise charges. Upgrade or downgrade anytime.",
      "pricing.monthly": "Monthly",
      "pricing.yearly": "Yearly",
      "pricing.save_30": "Save 30%",
      "pricing.free_name": "Free",
      "pricing.pro_name": "Pro",
      "pricing.studio_name": "Studio",
      "pricing.enterprise_name": "Enterprise",
      "pricing.free_cta": "Get Started Free",
      "pricing.pro_cta": "Start Pro Plan →",
      "pricing.studio_cta": "Start Studio Plan →",
      "pricing.enterprise_cta": "Contact Sales →",

      // 3D Studio
      "studio.file": "File",
      "studio.edit": "Edit",
      "studio.add": "Add",
      "studio.object": "Object",
      "studio.view": "View",
      "studio.render": "Render",
      "studio.save": "Save",
      "studio.saved": "Saved",
      "studio.saving": "Saving...",
      "studio.outliner": "Outliner",
      "studio.properties": "Properties",
      "studio.materials": "Materials",
      "studio.modifiers": "Modifiers",
      "studio.timeline": "Timeline",
      "studio.frame": "Frame",

      // Common
      "common.language": "Language",
      "common.loading": "Loading...",
      "common.cancel": "Cancel",
      "common.confirm": "Confirm",
      "common.save_changes": "Save changes",
      "common.delete": "Delete",
      "common.search": "Search"
    }
  };

  class DevForgeI18n {
    constructor() {
      this.supportedLangs = ['uz', 'ru', 'en'];
      this.currentLang = this.detectLanguage();
      this.init();
    }

    detectLanguage() {
      // 1. Check Cookie
      const match = document.cookie.match(/(?:^|;\s*)django_language=([^;]+)/);
      if (match && this.supportedLangs.includes(match[1])) return match[1];

      // 2. Check localStorage
      const local = localStorage.getItem('devforge_lang');
      if (local && this.supportedLangs.includes(local)) return local;

      // 3. Check document.documentElement lang
      const docLang = document.documentElement.lang;
      if (docLang && this.supportedLangs.includes(docLang)) return docLang;

      // 4. Default: uz
      return 'uz';
    }

    t(key, fallback = '') {
      const langDict = TRANSLATIONS[this.currentLang] || TRANSLATIONS['uz'];
      return langDict[key] || TRANSLATIONS['en']?.[key] || fallback || key;
    }

    setLanguage(lang, syncBackend = true) {
      if (!this.supportedLangs.includes(lang)) return;
      this.currentLang = lang;
      localStorage.setItem('devforge_lang', lang);
      document.cookie = `django_language=${lang};path=/;max-age=31536000;SameSite=Lax`;
      document.documentElement.lang = lang;

      // Apply translations to all DOM elements
      this.applyTranslations();
      this.updateLanguagePickers();

      // Sync with backend
      if (syncBackend) {
        fetch(`/set-language/${lang}/`, { method: 'GET' }).catch(() => {});
      }
    }

    applyTranslations() {
      // Update text nodes with data-i18n
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const translated = this.t(key);
        if (translated) el.textContent = translated;
      });

      // Update placeholders
      document.querySelectorAll('[data-i18n-ph]').forEach(el => {
        const key = el.getAttribute('data-i18n-ph');
        const translated = this.t(key);
        if (translated) el.placeholder = translated;
      });

      // Update titles
      document.querySelectorAll('[data-i18n-title]').forEach(el => {
        const key = el.getAttribute('data-i18n-title');
        const translated = this.t(key);
        if (translated) el.title = translated;
      });
    }

    updateLanguagePickers() {
      const labels = {
        uz: { name: "O'zbekcha", code: 'UZ' },
        ru: { name: 'Русский',   code: 'RU' },
        en: { name: 'English',   code: 'EN' }
      };
      const cur = labels[this.currentLang] || labels.uz;

      document.querySelectorAll('.lang-btn-current').forEach(el => {
        el.innerHTML = `🌐 <span class="lang-code">${cur.code}</span> <span class="lang-arrow" style="font-size:0.7rem;opacity:0.7;">▼</span>`;
      });

      document.querySelectorAll('.lang-opt-item').forEach(el => {
        const lang = el.getAttribute('data-lang');
        el.classList.toggle('active', lang === this.currentLang);
      });
    }

    init() {
      document.addEventListener('DOMContentLoaded', () => {
        this.applyTranslations();
        this.updateLanguagePickers();
      });
    }
  }

  window.devforgeI18n = new DevForgeI18n();
  window.t = (key, fallback) => window.devforgeI18n.t(key, fallback);
})();

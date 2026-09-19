/**
 * ══════════════════════════════════════════════════════════════════════════
 *  DEVFORGE ULTRA UNIVERSAL MULTI-LANGUAGE (i18n) ENGINE v3.0
 *  Dual-Engine: Instant Terminology Pre-Translator + Google Neural Bridge
 *  Supported Languages:
 *    - 'uz': O'zbekcha 🇺🇿 (Original / Asosiy)
 *    - 'ru': Русский   🇷🇺
 *    - 'en': English   🇬🇧
 * ══════════════════════════════════════════════════════════════════════════
 */

(function () {
  'use strict';

  // 1. Comprehensive Master Terminology Dictionary (350+ Critical UI Phrases)
  const DICTIONARY = [
    // Global Header & Navigation
    { uz: "Dashboard", ru: "Панель управления", en: "Dashboard" },
    { uz: "Feed", ru: "Лента", en: "Feed" },
    { uz: "Loyihalar", ru: "Проекты", en: "Projects" },
    { uz: "Jobs", ru: "Вакансии", en: "Jobs" },
    { uz: "Aktivlar", ru: "Ассеты", en: "Assets" },
    { uz: "Learn", ru: "Обучение", en: "Learn" },
    { uz: "Jams", ru: "Джемы", en: "Jams" },
    { uz: "🎮 Jams", ru: "🎮 Джемы", en: "🎮 Jams" },
    { uz: "Studio Suite", ru: "Студии", en: "Studio Suite" },
    { uz: "Community", ru: "Сообщество", en: "Community" },
    { uz: "Hamjamiyat", ru: "Сообщество", en: "Community" },
    { uz: "FAQ", ru: "Частые вопросы", en: "FAQ" },
    { uz: "Kirish", ru: "Войти", en: "Log in" },
    { uz: "Log in", ru: "Войти", en: "Log in" },
    { uz: "Qo'shilish", ru: "Регистрация", en: "Get Started" },
    { uz: "Get Started", ru: "Регистрация", en: "Get Started" },
    { uz: "Get Started Free", ru: "Начать бесплатно", en: "Get Started Free" },
    { uz: "Chiqish", ru: "Выйти", en: "Log out" },
    { uz: "Log out", ru: "Выйти", en: "Log out" },
    { uz: "Mening profilim", ru: "Мой профиль", en: "My Profile" },
    { uz: "Profilim", ru: "Мой профиль", en: "My Profile" },
    { uz: "Hamyon", ru: "Кошелек", en: "Wallet" },
    { uz: "Obuna", ru: "Подписка", en: "Subscription" },
    { uz: "Sozlamalar", ru: "Настройки", en: "Settings" },
    { uz: "Boshqaruv paneli", ru: "Панель управления", en: "Dashboard" },
    { uz: "Qidirish...", ru: "Поиск...", en: "Search..." },
    { uz: "Qidiruv", ru: "Поиск", en: "Search" },

    // Studios Suite
    { uz: "🎨 3D Studio", ru: "🎨 3D Студия", en: "🎨 3D Studio" },
    { uz: "3D Studio", ru: "3D Студия", en: "3D Studio" },
    { uz: "🖼️ Image Editor", ru: "🖼️ Графический редактор", en: "🖼️ Image Editor" },
    { uz: "Image Editor", ru: "Графический редактор", en: "Image Editor" },
    { uz: "🎵 Audio Lab", ru: "🎵 Аудио лаборатория", en: "🎵 Audio Lab" },
    { uz: "Audio Lab", ru: "Аудио лаборатория", en: "Audio Lab" },
    { uz: "🎬 Video Lab", ru: "🎬 Видео лаборатория", en: "🎬 Video Lab" },
    { uz: "Video Lab", ru: "Видео лаборатория", en: "Video Lab" },
    { uz: "🏰 World Builder", ru: "🏰 Конструктор миров", en: "🏰 World Builder" },
    { uz: "World Builder", ru: "Конструктор миров", en: "World Builder" },
    { uz: "🎮 Game Engine", ru: "🎮 Игровой движок", en: "🎮 Game Engine" },
    { uz: "Game Engine", ru: "Игровой движок", en: "Game Engine" },
    { uz: "⚙️ Dev Settings", ru: "⚙️ Настройки разработчика", en: "⚙️ Dev Settings" },
    { uz: "Dev Settings", ru: "Настройки разработчика", en: "Dev Settings" },
    { uz: "Developer Settings", ru: "Настройки разработчика", en: "Developer Settings" },
    { uz: "DEVELOPER SETTINGS", ru: "НАСТРОЙКИ РАЗРАБОТЧИКА", en: "DEVELOPER SETTINGS" },
    { uz: "Platform Control Panel", ru: "Панель управления платформой", en: "Platform Control Panel" },

    // Marketplace / Assets
    { uz: "DIGITAL ASSETS", ru: "ЦИФРОВЫЕ АССЕТЫ", en: "DIGITAL ASSETS" },
    { uz: "Asset Marketplace", ru: "Маркетплейс ассетов", en: "Asset Marketplace" },
    { uz: "Mening Aktivlarim", ru: "Мои ассеты", en: "My Assets" },
    { uz: "📁 Mening Aktivlarim", ru: "📁 Мои ассеты", en: "📁 My Assets" },
    { uz: "Moderatsiya", ru: "Модерация", en: "Moderation" },
    { uz: "🛡️ Moderatsiya", ru: "🛡️ Модерация", en: "🛡️ Moderation" },
    { uz: "Aktiv Yuklash", ru: "Загрузить ассет", en: "Upload Asset" },
    { uz: "⬆️ Aktiv Yuklash", ru: "⬆️ Загрузить ассет", en: "⬆️ Upload Asset" },
    { uz: "All Assets", ru: "Все ассеты", en: "All Assets" },
    { uz: "Barcha aktivlar", ru: "Все ассеты", en: "All Assets" },
    { uz: "Search models, materials, tags...", ru: "Поиск моделей, материалов, тегов...", en: "Search models, materials, tags..." },
    { uz: "Modellar, materiallar, teglarni qidirish...", ru: "Поиск моделей, материалов, тегов...", en: "Search models, materials, tags..." },
    { uz: "Any Price", ru: "Любая цена", en: "Any Price" },
    { uz: "Ixtiyoriy narx", ru: "Любая цена", en: "Any Price" },
    { uz: "Free", ru: "Бесплатно", en: "Free" },
    { uz: "Bepul", ru: "Бесплатно", en: "Free" },
    { uz: "Paid", ru: "Платные", en: "Paid" },
    { uz: "Pullik", ru: "Платные", en: "Paid" },
    { uz: "Any Format", ru: "Любой формат", en: "Any Format" },
    { uz: "Ixtiyoriy format", ru: "Любой формат", en: "Any Format" },
    { uz: "Apply Filters", ru: "Применить фильтры", en: "Apply Filters" },
    { uz: "Filtrlarni qo'llash", ru: "Применить фильтры", en: "Apply Filters" },
    { uz: "Reset", ru: "Сбросить", en: "Reset" },
    { uz: "Tozalash", ru: "Сбросить", en: "Reset" },
    { uz: "No assets found", ru: "Ассеты не найдены", en: "No assets found" },
    { uz: "Aktivlar topilmadi", ru: "Ассеты не найдены", en: "No assets found" },
    { uz: "Download", ru: "Скачать", en: "Download" },
    { uz: "Yuklab olish", ru: "Скачать", en: "Download" },
    { uz: "Buy Now", ru: "Купить сейчас", en: "Buy Now" },
    { uz: "Sotib olish", ru: "Купить", en: "Buy Now" },
    { uz: "Free Download", ru: "Скачать бесплатно", en: "Free Download" },
    { uz: "Bepul yuklab olish", ru: "Скачать бесплатно", en: "Free Download" },

    // Projects & Collaboration
    { uz: "Discover Projects", ru: "Обзор проектов", en: "Discover Projects" },
    { uz: "+ Create New Project", ru: "+ Создать новый проект", en: "+ Create New Project" },
    { uz: "Yangi loyiha yaratish", ru: "+ Создать новый проект", en: "+ Create New Project" },
    { uz: "All Genres", ru: "Все жанры", en: "All Genres" },
    { uz: "Barcha janrlar", ru: "Все жанры", en: "All Genres" },
    { uz: "All Statuses", ru: "Все статусы", en: "All Statuses" },
    { uz: "Barcha holatlar", ru: "Все статусы", en: "All Statuses" },
    { uz: "Filter", ru: "Фильтр", en: "Filter" },
    { uz: "Filtrlash", ru: "Фильтр", en: "Filter" },
    { uz: "No projects found", ru: "Проекты не найдены", en: "No projects found" },
    { uz: "Loyihalar topilmadi", ru: "Проекты не найдены", en: "No projects found" },
    { uz: "Jamoaga Qo'shilish", ru: "Вступить в команду", en: "Join Team" },
    { uz: "Ariza ko'rib chiqilmoqda...", ru: "Заявка на рассмотрении...", en: "Application pending..." },
    { uz: "📋 Vazifalar", ru: "📋 Задачи", en: "📋 Tasks" },
    { uz: "Vazifalar", ru: "Задачи", en: "Tasks" },
    { uz: "+ Vazifa", ru: "+ Задача", en: "+ Task" },
    { uz: "📌 Kutilmoqda", ru: "📌 Ожидает", en: "📌 To Do" },
    { uz: "⚡ Jarayonda", ru: "⚡ В процессе", en: "⚡ In Progress" },
    { uz: "✅ Bajarildi", ru: "✅ Завершено", en: "✅ Done" },
    { uz: "👥 Jamoa A'zolari", ru: "👥 Участники команды", en: "👥 Team Members" },
    { uz: "Jamoa a'zolari", ru: "Участники команды", en: "Team Members" },
    { uz: "Egasi", ru: "Владелец", en: "Owner" },
    { uz: "a'zo", ru: "участник", en: "member" },

    // Export & Downloads
    { uz: "📤 Export (ZIP)", ru: "📤 Экспорт (ZIP)", en: "📤 Export (ZIP)" },
    { uz: "📤 ZIP Export", ru: "📤 ZIP Экспорт", en: "📤 ZIP Export" },
    { uz: "📤 ZIP Export Qilish", ru: "📤 Экспортировать в ZIP", en: "📤 Export as ZIP" },
    { uz: "📤 Loyihani Export Qilish (ZIP)", ru: "📤 Экспорт проекта (ZIP)", en: "📤 Export Project (ZIP)" },
    { uz: "Loyihani export qilish", ru: "Экспорт проекта", en: "Export Project" },
    { uz: "📦 Loyiha Export (ZIP)", ru: "📦 Экспорт проекта (ZIP)", en: "📦 Project Export (ZIP)" },
    { uz: "📁 Loyiha Fayllari", ru: "📁 Файлы проекта", en: "📁 Project Files" },
    { uz: "Loyiha Fayllari", ru: "Файлы проекта", en: "Project Files" },
    { uz: "Workspace fayllari:", ru: "Файлы рабочей области:", en: "Workspace files:" },
    { uz: "Arxivni Yangilash", ru: "Обновить архив", en: "Update Archive" },
    { uz: "Arxiv Yuklash", ru: "Загрузить архив", en: "Upload Archive" },
    { uz: "Export: Ochiq", ru: "Экспорт: Открыт", en: "Export: Open" },
    { uz: "Export: Yopiq", ru: "Экспорт: Закрыт", en: "Export: Closed" },
    { uz: "🟢 Export Ochiq", ru: "🟢 Экспорт Открыт", en: "🟢 Export Open" },
    { uz: "🔴 Export Yopiq", ru: "🔴 Экспорт Закрыт", en: "🔴 Export Closed" },
    { uz: "⭐ Export (Obuna Kerak)", ru: "⭐ Экспорт (Требуется подписка)", en: "⭐ Export (Subscription Required)" },
    { uz: "⭐ ZIP Export (Obuna kerak)", ru: "⭐ Экспорт ZIP (Нужна подписка)", en: "⭐ ZIP Export (Subscription Required)" },
    { uz: "🔒 Ega Ruxsati Kerak", ru: "🔒 Требуется разрешение", en: "🔒 Owner Permission Required" },
    { uz: "🔒 Export Yopiq", ru: "🔒 Экспорт закрыт", en: "🔒 Export Closed" },
    { uz: "👤 Foydalanuvchiga Export Ruxsatini Berish:", ru: "👤 Выдать разрешение на экспорт:", en: "👤 Grant Export Permission:" },
    { uz: "+ Berish", ru: "+ Выдать", en: "+ Grant" },
    { uz: "Ruxsat berilganlar", ru: "Разрешено для", en: "Permitted users" },
    { uz: "✕ O'chirish", ru: "✕ Отозвать", en: "✕ Revoke" },
    { uz: "✓ Ruxsat bor", ru: "✓ Разрешено", en: "✓ Permitted" },
    { uz: "+ Ruxsat", ru: "+ Разрешить", en: "+ Permission" },
    { uz: "💻 Workspace'da ochish", ru: "💻 Открыть в Workspace", en: "💻 Open in Workspace" },

    // Common Buttons & Actions
    { uz: "Saqlash", ru: "Сохранить", en: "Save" },
    { uz: "💾 Saqlash", ru: "💾 Сохранить", en: "💾 Save" },
    { uz: "Bekor qilish", ru: "Отмена", en: "Cancel" },
    { uz: "O'chirish", ru: "Удалить", en: "Delete" },
    { uz: "Yuklash", ru: "Загрузить", en: "Upload" },
    { uz: "Yaratish", ru: "Создать", en: "Create" },
    { uz: "Qo'shish", ru: "Добавить", en: "Add" },
    { uz: "+ Qo'shish", ru: "+ Добавить", en: "+ Add" },
    { uz: "Yangilash", ru: "Обновить", en: "Update" },
    { uz: "Tahrirlash", ru: "Редактировать", en: "Edit" },
    { uz: "Batafsil", ru: "Подробнее", en: "Details" },
    { uz: "Explore", ru: "Обзор", en: "Explore" },
    { uz: "Ko'rish", ru: "Просмотр", en: "View" },
    { uz: "Yuborish", ru: "Отправить", en: "Send" },
    { uz: "Ariza Yuborish", ru: "Отправить заявку", en: "Submit Application" },
    { uz: "✓ Qabul qilish", ru: "✓ Принять", en: "✓ Accept" },
    { uz: "Rad etish", ru: "Отклонить", en: "Reject" },
    { uz: "Tasdiqlash", ru: "Подтвердить", en: "Confirm" },
    { uz: "Boshlash", ru: "Начать", en: "Start" },
    { uz: "Tugatish", ru: "Завершить", en: "Complete" },
    { uz: "✓ Tugatish", ru: "✓ Завершить", en: "✓ Complete" },
    { uz: "Obunani Ko'rish", ru: "Посмотреть подписки", en: "View Subscriptions" },

    // Statuses & Badges
    { uz: "Aktiv", ru: "Активный", en: "Active" },
    { uz: "Faol", ru: "Активный", en: "Active" },
    { uz: "Rejalashtirish", ru: "Планирование", en: "Planning" },
    { uz: "Yakunlangan", ru: "Завершен", en: "Completed" },
    { uz: "To'xtatilgan", ru: "Приостановлен", en: "Paused" },
    { uz: "Ochiq", ru: "Открытый", en: "Public" },
    { uz: "Yopiq", ru: "Закрытый", en: "Private" },
    { uz: "Taklif bilan", ru: "По приглашению", en: "Invite Only" },
    { uz: "Yuqori", ru: "Высокий", en: "High" },
    { uz: "O'rta", ru: "Средний", en: "Medium" },
    { uz: "Past", ru: "Низкий", en: "Low" },
    { uz: "Muvaffaqiyatli", ru: "Успешно", en: "Successful" },
    { uz: "Xatolik", ru: "Ошибка", en: "Error" },

    // Genres & Tech
    { uz: "Strategiya", ru: "Стратегия", en: "Strategy" },
    { uz: "Simulyatsiya", ru: "Симуляция", en: "Simulation" },
    { uz: "Boshqa", ru: "Другое", en: "Other" },

    // Feed & Community
    { uz: "Post yaratish", ru: "Создать пост", en: "Create Post" },
    { uz: "Nima yangiliklar?", ru: "Что нового?", en: "What's new?" },
    { uz: "Ulashish", ru: "Поделиться", en: "Share" },
    { uz: "Izoh qoldirish", ru: "Оставить комментарий", en: "Leave a comment" },
    { uz: "Izohlar", ru: "Комментарии", en: "Comments" },
    { uz: "Obunachilar", ru: "Подписчики", en: "Followers" },
    { uz: "Kuzatish", ru: "Подписаться", en: "Follow" },
    { uz: "Kuzatilyapti", ru: "Вы подписаны", en: "Following" },

    // Roles
    { uz: "O'yin Dasturchisi", ru: "Гейм-разработчик", en: "Game Developer" },
    { uz: "Dasturchi", ru: "Разработчик", en: "Developer" },
    { uz: "3D Rassom", ru: "3D Художник", en: "3D Artist" },
    { uz: "Dizayner", ru: "Дизайнер", en: "Designer" },
    { uz: "UI/UX Dizayner", ru: "UI/UX Дизайнер", en: "UI/UX Designer" },
    { uz: "Musiqa/Ovoz", ru: "Звук / Музыка", en: "Audio / Sound" },
    { uz: "Stsenariy Yozuvchi", ru: "Сценарист", en: "Writer" }
  ];

  // 2. Build Fast Exact-Match Map
  function normalise(str) {
    if (!str) return '';
    return str.toString().replace(/\s+/g, ' ').trim();
  }

  const PHRASE_MAP = new Map();
  DICTIONARY.forEach(item => {
    ['uz', 'ru', 'en'].forEach(lang => {
      const val = item[lang];
      if (val) {
        const norm = normalise(val);
        if (norm) {
          PHRASE_MAP.set(norm, item);
          PHRASE_MAP.set(norm.toLowerCase(), item);
        }
      }
    });
  });

  // 3. DevForgeI18n Engine Definition
  class DevForgeI18n {
    constructor() {
      this.supported = ['uz', 'ru', 'en'];
      this.currentLang = this.detectLanguage();
      this.isGoogleReady = false;
      this.setupGoogleStyles();
      this.init();
    }

    detectLanguage() {
      // 1. Check Cookie
      const match = document.cookie.match(/(?:^|;\s*)django_language=([^;]+)/);
      if (match && this.supported.includes(match[1])) return match[1];

      // 2. Check googtrans cookie
      const gmatch = document.cookie.match(/(?:^|;\s*)googtrans=(?:%2F|\/)(?:[a-zA-Z_-]+)(?:%2F|\/)([a-zA-Z_-]+)/);
      if (gmatch && this.supported.includes(gmatch[1])) return gmatch[1];

      // 3. Check localStorage
      try {
        const local = localStorage.getItem('devforge_lang');
        if (local && this.supported.includes(local)) return local;
      } catch (e) {}

      // 4. Default
      return 'uz';
    }

    setupGoogleStyles() {
      // Ensure Google Translate banners & toolbars are completely hidden
      if (document.getElementById('df-google-i18n-styles')) return;
      const st = document.createElement('style');
      st.id = 'df-google-i18n-styles';
      st.textContent = `
        .goog-te-banner-frame, .goog-te-banner-frame.skiptranslate, #goog-gt-tt, .goog-te-balloon-frame {
          display: none !important;
          visibility: hidden !important;
        }
        body {
          top: 0px !important;
          position: static !important;
        }
        #google_translate_element {
          display: none !important;
        }
        .goog-text-highlight {
          background: none !important;
          box-shadow: none !important;
        }
        font[style] {
          background: transparent !important;
          box-shadow: none !important;
        }
      `;
      (document.head || document.documentElement).appendChild(st);
    }

    injectGoogleTranslate() {
      if (window.google && window.google.translate) {
        this.isGoogleReady = true;
        this.syncGoogleEngine();
        return;
      }

      // Ensure container exists
      let container = document.getElementById('google_translate_element');
      if (!container) {
        container = document.createElement('div');
        container.id = 'google_translate_element';
        container.style.display = 'none';
        document.body.appendChild(container);
      }

      // Global Callback
      window.devforgeGoogleTranslateInit = () => {
        try {
          new window.google.translate.TranslateElement({
            pageLanguage: 'uz',
            includedLanguages: 'uz,ru,en',
            autoDisplay: false
          }, 'google_translate_element');
          this.isGoogleReady = true;
          setTimeout(() => this.syncGoogleEngine(), 100);
        } catch (err) {
          console.warn('[i18n] Google init error:', err);
        }
      };

      // Load Script
      if (!document.getElementById('df-gt-script')) {
        const script = document.createElement('script');
        script.id = 'df-gt-script';
        script.src = 'https://translate.google.com/translate_a/element.js?cb=devforgeGoogleTranslateInit';
        script.async = true;
        document.body.appendChild(script);
      }
    }

    syncGoogleEngine() {
      const lang = this.currentLang;
      if (lang === 'uz') {
        // Reset to original
        this.clearGoogCookie();
        const combo = document.querySelector('#google_translate_element select.goog-te-combo');
        if (combo && combo.value) {
          combo.value = 'uz';
          combo.dispatchEvent(new Event('change'));
        }
        return;
      }

      // Set cookie for Google Translate
      const val = `/uz/${lang}`;
      document.cookie = `googtrans=${val};path=/;max-age=31536000`;
      const domainParts = window.location.hostname.split('.');
      if (domainParts.length > 1) {
        const rootDomain = '.' + domainParts.slice(-2).join('.');
        document.cookie = `googtrans=${val};path=/;domain=${rootDomain};max-age=31536000`;
      }

      // Trigger combo if present
      const combo = document.querySelector('#google_translate_element select.goog-te-combo');
      if (combo) {
        if (combo.value !== lang) {
          combo.value = lang;
          combo.dispatchEvent(new Event('change'));
        }
      } else {
        // Retry shortly until loaded
        setTimeout(() => {
          const c2 = document.querySelector('#google_translate_element select.goog-te-combo');
          if (c2 && c2.value !== lang) {
            c2.value = lang;
            c2.dispatchEvent(new Event('change'));
          }
        }, 300);
      }
    }

    clearGoogCookie() {
      document.cookie = 'googtrans=;path=/;expires=Thu, 01 Jan 1970 00:00:00 UTC';
      const domainParts = window.location.hostname.split('.');
      if (domainParts.length > 1) {
        const rootDomain = '.' + domainParts.slice(-2).join('.');
        document.cookie = `googtrans=;path=/;domain=${rootDomain};expires=Thu, 01 Jan 1970 00:00:00 UTC`;
      }
    }

    setLanguage(lang, syncBackend = true) {
      if (!this.supported.includes(lang)) return;
      const prevLang = this.currentLang;
      this.currentLang = lang;

      // 1. Persist in Storage
      try {
        localStorage.setItem('devforge_lang', lang);
      } catch (e) {}

      // 2. Set Cookies
      document.cookie = `django_language=${lang};path=/;max-age=31536000;SameSite=Lax`;
      document.documentElement.lang = lang;

      // 3. Instant UI updates
      this.updateLanguagePickers();

      // 4. Instant Local Pre-Translate
      this.preTranslateDOM();

      // 5. Google Translate Neural Engine
      if (lang === 'uz') {
        this.clearGoogCookie();
        // If we were translated, reload or reset combo to get clean original Uzbek
        const combo = document.querySelector('#google_translate_element select.goog-te-combo');
        if (combo) {
          combo.value = 'uz';
          combo.dispatchEvent(new Event('change'));
        }
        if (prevLang !== 'uz') {
          // A clean page refresh ensures 100% restoration of pristine Uzbek text
          setTimeout(() => { window.location.reload(); }, 150);
        }
      } else {
        this.syncGoogleEngine();
      }

      // 6. Backend Sync
      if (syncBackend) {
        fetch(`/set-language/${lang}/?format=json`, {
          method: 'GET',
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        }).catch(() => {});
      }
    }

    translateText(text) {
      const norm = normalise(text);
      if (!norm) return null;
      const match = PHRASE_MAP.get(norm) || PHRASE_MAP.get(norm.toLowerCase());
      if (match && match[this.currentLang]) {
        return match[this.currentLang];
      }
      return null;
    }

    preTranslateDOM(root = document.body) {
      if (!root || this.currentLang === 'uz') return;

      try {
        // Walk all text nodes
        const walker = document.createTreeWalker(
          root,
          NodeFilter.SHOW_TEXT,
          {
            acceptNode: (node) => {
              if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
              const p = node.parentElement;
              if (!p) return NodeFilter.FILTER_REJECT;
              const tag = p.tagName.toLowerCase();
              if (['script', 'style', 'code', 'pre', 'textarea'].includes(tag)) return NodeFilter.FILTER_REJECT;
              if (p.closest('#langMenu') || p.closest('#homeLangMenu') || p.closest('.lang-switcher-wrap') || p.classList.contains('notranslate')) {
                return NodeFilter.FILTER_REJECT;
              }
              return NodeFilter.FILTER_ACCEPT;
            }
          },
          false
        );

        const nodes = [];
        let curr;
        while ((curr = walker.nextNode())) {
          nodes.push(curr);
        }

        nodes.forEach(node => {
          const raw = node.nodeValue;
          const trimmed = normalise(raw);
          if (!trimmed) return;

          if (!node._dfOrig) {
            node._dfOrig = trimmed;
          }
          const trans = this.translateText(node._dfOrig);
          if (trans) {
            const leading = raw.match(/^\s*/)[0];
            const trailing = raw.match(/\s*$/)[0];
            node.nodeValue = leading + trans + trailing;
          }
        });

        // Translate Placeholders
        document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(el => {
          if (!el._dfOrigPh) el._dfOrigPh = el.placeholder;
          const trans = this.translateText(el._dfOrigPh);
          if (trans) el.placeholder = trans;
        });

        // Translate Buttons
        document.querySelectorAll('input[type="button"], input[type="submit"]').forEach(btn => {
          if (!btn._dfOrigVal) btn._dfOrigVal = btn.value;
          const trans = this.translateText(btn._dfOrigVal);
          if (trans) btn.value = trans;
        });
      } catch (err) {
        console.warn('[i18n] Pre-translate error:', err);
      }
    }

    updateLanguagePickers() {
      const code = (this.currentLang || 'uz').toUpperCase();

      // Update button text
      document.querySelectorAll('.lang-btn-current .lang-code').forEach(el => {
        el.textContent = code;
      });

      // Update options
      document.querySelectorAll('.lang-opt-item').forEach(el => {
        const itemLang = el.getAttribute('data-lang');
        const isActive = (itemLang === this.currentLang);
        el.classList.toggle('active', isActive);
        const chk = el.querySelector('.lang-chk');
        if (chk) chk.style.display = isActive ? 'inline' : 'none';
      });
    }

    observeDynamic() {
      if (!window.MutationObserver) return;
      let timer = null;
      const obs = new MutationObserver((mutations) => {
        let hasNew = false;
        for (const m of mutations) {
          if (m.type === 'childList' && m.addedNodes.length > 0) {
            hasNew = true;
            break;
          }
        }
        if (hasNew) {
          clearTimeout(timer);
          timer = setTimeout(() => {
            this.preTranslateDOM();
          }, 80);
        }
      });

      obs.observe(document.body, { childList: true, subtree: true });
    }

    init() {
      const start = () => {
        this.updateLanguagePickers();
        if (this.currentLang !== 'uz') {
          this.preTranslateDOM();
        }
        this.injectGoogleTranslate();
        this.observeDynamic();
      };

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
      } else {
        start();
      }
    }
  }

  // Initialise Global Instance
  window.devforgeI18n = new DevForgeI18n();

  // Helper for manual language switching anywhere
  window.changeLanguage = function (lang) {
    if (window.devforgeI18n) {
      window.devforgeI18n.setLanguage(lang);
    }
  };
})();

/**
 * ═════════════════════════════════════════════════════════════════
 *  DEVFORGE UNIVERSAL MULTI-LANGUAGE (i18n) ENGINE
 *  Supported Languages:
 *    - 'uz': O'zbekcha 🇺🇿
 *    - 'ru': Русский   🇷🇺
 *    - 'en': English   🇬🇧
 * ═════════════════════════════════════════════════════════════════
 */

(function() {
  'use strict';

  // 1. Comprehensive Master Dictionary (Exact Phrase Pairs)
  const DICTIONARY = [
    // Navigation & Global Header
    { uz: "Dashboard", ru: "Панель управления", en: "Dashboard" },
    { uz: "Feed", ru: "Лента", en: "Feed" },
    { uz: "Loyihalar", ru: "Проекты", en: "Projects" },
    { uz: "Jobs", ru: "Вакансии", en: "Jobs" },
    { uz: "Aktivlar", ru: "Ассеты", en: "Assets" },
    { uz: "Learn", ru: "Обучение", en: "Learn" },
    { uz: "Jams", ru: "Джемы", en: "Jams" },
    { uz: "🎮 Jams", ru: "🎮 Джемы", en: "🎮 Jams" },
    { uz: "Studio Suite", ru: "Студии", en: "Studio Suite" },
    { uz: "⚙️ Dev Settings", ru: "⚙️ Настройки разработчика", en: "⚙️ Dev Settings" },
    { uz: "Dev Settings", ru: "Настройки разработчика", en: "Dev Settings" },
    { uz: "DEVELOPER SETTINGS", ru: "НАСТРОЙКИ РАЗРАБОТЧИКА", en: "DEVELOPER SETTINGS" },
    { uz: "Platform Control Panel", ru: "Панель управления платформой", en: "Platform Control Panel" },
    { uz: "Kirish", ru: "Вход", en: "Log in" },
    { uz: "Qo'shilish", ru: "Регистрация", en: "Get Started" },
    { uz: "Chiqish", ru: "Выйти", en: "Log out" },
    { uz: "Mening profilim", ru: "Мой профиль", en: "My Profile" },
    { uz: "Profilim", ru: "Мой профиль", en: "My Profile" },
    { uz: "Hamyon", ru: "Кошелек", en: "Wallet" },
    { uz: "Obuna", ru: "Подписка", en: "Subscription" },
    { uz: "Boshqaruv paneli", ru: "Панель управления", en: "Dashboard" },
    { uz: "Qidirish...", ru: "Поиск...", en: "Search..." },

    // Studios List
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

    // Asset Marketplace (Shown in screenshot)
    { uz: "DIGITAL ASSETS", ru: "ЦИФРОВЫЕ АССЕТЫ", en: "DIGITAL ASSETS" },
    { uz: "Asset Marketplace", ru: "Маркетплейс ассетов", en: "Asset Marketplace" },
    { 
      uz: "High-fidelity 3D models, textures, and UI kits ready for your next project. Built for Unreal Engine, Unity, and Godot.",
      ru: "Высококачественные 3D модели, текстуры и UI наборы для вашего проекта. Готовы для Unreal Engine, Unity и Godot.",
      en: "High-fidelity 3D models, textures, and UI kits ready for your next project. Built for Unreal Engine, Unity, and Godot."
    },
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
    { uz: "Buy Now", ru: "Купить", en: "Buy Now" },
    { uz: "Sotib olish", ru: "Купить", en: "Buy Now" },
    { uz: "Free Download", ru: "Бесплатно скачать", en: "Free Download" },
    { uz: "Bepul yuklab olish", ru: "Бесплатно скачать", en: "Free Download" },
    { uz: "Upload New Asset", ru: "Загрузить новый ассет", en: "Upload New Asset" },
    { uz: "Yangi aktiv yuklash", ru: "Загрузить новый ассет", en: "Upload New Asset" },

    // Common Actions & Buttons
    { uz: "Saqlash", ru: "Сохранить", en: "Save" },
    { uz: "💾 Saqlash", ru: "💾 Сохранить", en: "💾 Save" },
    { uz: "O'chirish", ru: "Удалить", en: "Delete" },
    { uz: "🗑️ O'chirish", ru: "🗑️ Удалить", en: "🗑️ Delete" },
    { uz: "Bekor qilish", ru: "Отмена", en: "Cancel" },
    { uz: "Tasdiqlash", ru: "Подтвердить", en: "Confirm" },
    { uz: "Tahrirlash", ru: "Редактировать", en: "Edit" },
    { uz: "Yaratish", ru: "Создать", en: "Create" },
    { uz: "Qo'shish", ru: "Добавить", en: "Add" },
    { uz: "Yopish", ru: "Закрыть", en: "Close" },
    { uz: "Yuklanmoqda...", ru: "Загрузка...", en: "Loading..." },
    { uz: "Muvaffaqiyatli saqlandi", ru: "Успешно сохранено", en: "Saved successfully" },
    { uz: "Ko'rish", ru: "Просмотр", en: "View" },
    { uz: "Batafsil", ru: "Подробнее", en: "Details" },
    { uz: "Orqaga", ru: "Назад", en: "Back" },
    { uz: "Keyingisi", ru: "Далее", en: "Next" },
    { uz: "Barchasi", ru: "Все", en: "All" },
    { uz: "Yordam", ru: "Помощь", en: "Help" },
    { uz: "Sozlamalar", ru: "Настройки", en: "Settings" },

    // Developer Settings Specific
    { uz: "Ro'yxatdan o'tgan foydalanuvchilar", ru: "Зарегистрированные пользователи", en: "Registered users" },
    { uz: "Platformadagi barcha loyihalar", ru: "Все проекты на платформе", en: "All projects on the platform" },
    { uz: "Marketplace aktiv resurslari", ru: "Ассеты маркетплейса", en: "Marketplace assets" },
    { uz: "Tasdiqlash kutilayotgan aktivlar", ru: "Ассеты на модерации", en: "Pending approval assets" },
    { uz: "Barchasini yoqish", ru: "Включить все", en: "Enable All" },
    { uz: "🟢 Barchasini yoqish", ru: "🟢 Включить все", en: "🟢 Enable All" },
    { uz: "Barchasini yashirish", ru: "Скрыть все", en: "Disable All" },
    { uz: "🔴 Barchasini yashirish", ru: "🔴 Скрыть все", en: "🔴 Disable All" },
    { uz: "Ko'rsatish", ru: "Показать", en: "Show" },
    { uz: "Yashirish", ru: "Скрыть", en: "Hide" },
    { uz: "● KO'RINADI", ru: "● ВИДЕН", en: "● VISIBLE" },
    { uz: "○ YASHIRILGAN", ru: "○ СКРЫТ", en: "○ HIDDEN" },
    { uz: "Ochib ko'rish ↗", ru: "Открыть ↗", en: "Open ↗" },

    // Projects & Dashboard
    { uz: "Mening Loyihalarim", ru: "Мои проекты", en: "My Projects" },
    { uz: "Yangi Loyiha", ru: "Новый проект", en: "New Project" },
    { uz: "Yangi Loyiha Yaratish", ru: "Создать новый проект", en: "Create New Project" },
    { uz: "Loyiha Nomi", ru: "Название проекта", en: "Project Name" },
    { uz: "Tavsif", ru: "Описание", en: "Description" },
    { uz: "A'zolar", ru: "Участники", en: "Members" },
    { uz: "Holat", ru: "Статус", en: "Status" },

    // Landing / Home page
    { uz: "Vositalar", ru: "Инструменты", en: "Tools" },
    { uz: "Imkoniyatlar", ru: "Возможности", en: "Features" },
    { uz: "Tariflar", ru: "Тарифы", en: "Pricing" },
    { uz: "Savol-Javob", ru: "FAQ", en: "FAQ" },
    { uz: "Hamjamiyat", ru: "Сообщество", en: "Community" },
    { uz: "Bepul boshlash", ru: "Начать бесплатно", en: "Get Started Free" },
    { uz: "Bepul Boshlash", ru: "Начать бесплатно", en: "Get Started Free" }
  ];

  // 2. Build Fast Normalised Lookup Map
  // Key format: normalised_text -> { uz, ru, en }
  const EXACT_MAP = new Map();

  function normalise(str) {
    if (!str) return '';
    return str.toString().replace(/\s+/g, ' ').trim();
  }

  DICTIONARY.forEach(entry => {
    ['uz', 'ru', 'en'].forEach(lang => {
      const val = entry[lang];
      if (val) {
        const norm = normalise(val);
        if (norm) {
          EXACT_MAP.set(norm, entry);
          EXACT_MAP.set(norm.toLowerCase(), entry);
        }
      }
    });
  });

  // 3. Main DevForgeI18n Engine
  class DevForgeI18n {
    constructor() {
      this.supportedLangs = ['uz', 'ru', 'en'];
      this.currentLang = this.detectLanguage();
      this.isTranslating = false;
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

    setLanguage(lang, syncBackend = true) {
      if (!this.supportedLangs.includes(lang)) return;
      this.currentLang = lang;
      try {
        localStorage.setItem('devforge_lang', lang);
      } catch(e) {}
      document.cookie = `django_language=${lang};path=/;max-age=31536000;SameSite=Lax`;
      document.documentElement.lang = lang;

      // Execute full DOM translation immediately
      this.translateFullDOM();
      this.updateLanguagePickers();

      // Sync with backend via fetch
      if (syncBackend) {
        fetch(`/set-language/${lang}/`, { method: 'GET' }).catch(() => {});
      }
    }

    translateText(text) {
      const norm = normalise(text);
      if (!norm) return null;

      // Check exact match
      let match = EXACT_MAP.get(norm) || EXACT_MAP.get(norm.toLowerCase());
      if (match && match[this.currentLang]) {
        return match[this.currentLang];
      }
      return null;
    }

    translateFullDOM(root = document.body) {
      if (!root || this.isTranslating) return;
      this.isTranslating = true;

      try {
        // A. Process all data-i18n attributes first
        document.querySelectorAll('[data-i18n]').forEach(el => {
          const key = el.getAttribute('data-i18n');
          const trans = this.translateText(key);
          if (trans) el.textContent = trans;
        });

        // B. Process input/textarea placeholders
        document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(input => {
          const orig = input.getAttribute('data-orig-ph') || input.placeholder;
          if (!input.hasAttribute('data-orig-ph')) {
            input.setAttribute('data-orig-ph', orig);
          }
          const trans = this.translateText(orig);
          if (trans) input.placeholder = trans;
        });

        // C. Process input values (buttons like value="Filtrlash")
        document.querySelectorAll('input[type="button"], input[type="submit"]').forEach(btn => {
          const orig = btn.getAttribute('data-orig-val') || btn.value;
          if (!btn.hasAttribute('data-orig-val')) {
            btn.setAttribute('data-orig-val', orig);
          }
          const trans = this.translateText(orig);
          if (trans) btn.value = trans;
        });

        // D. Walk all Text Nodes in the DOM
        const walker = document.createTreeWalker(
          root,
          NodeFilter.SHOW_TEXT,
          {
            acceptNode: (node) => {
              if (!node.nodeValue || !node.nodeValue.trim()) {
                return NodeFilter.FILTER_REJECT;
              }
              const parent = node.parentElement;
              if (!parent) return NodeFilter.FILTER_REJECT;
              const tag = parent.tagName.toLowerCase();
              if (['script', 'style', 'code', 'pre', 'textarea'].includes(tag)) {
                return NodeFilter.FILTER_REJECT;
              }
              if (parent.closest('#langMenu') || parent.closest('.lang-switcher-wrap')) {
                return NodeFilter.FILTER_REJECT;
              }
              return NodeFilter.FILTER_ACCEPT;
            }
          },
          false
        );

        const nodesToTranslate = [];
        let currNode;
        while ((currNode = walker.nextNode())) {
          nodesToTranslate.push(currNode);
        }

        nodesToTranslate.forEach(node => {
          const raw = node.nodeValue;
          const trimmed = normalise(raw);
          if (!trimmed) return;

          // If node has original stored in parent
          let orig = node._origText || trimmed;
          if (!node._origText) {
            node._origText = trimmed;
          }

          const trans = this.translateText(orig);
          if (trans) {
            // Preserve leading and trailing whitespace
            const leading = raw.match(/^\s*/)[0];
            const trailing = raw.match(/\s*$/)[0];
            node.nodeValue = leading + trans + trailing;
          }
        });

        // E. Also translate titles and aria-labels
        document.querySelectorAll('[title]').forEach(el => {
          if (el.closest('#langMenu')) return;
          const orig = el.getAttribute('data-orig-title') || el.title;
          if (!el.hasAttribute('data-orig-title')) {
            el.setAttribute('data-orig-title', orig);
          }
          const trans = this.translateText(orig);
          if (trans) el.title = trans;
        });

      } catch (err) {
        console.warn("[i18n] Translation error:", err);
      } finally {
        this.isTranslating = false;
      }
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
        const isCur = (lang === this.currentLang);
        el.classList.toggle('active', isCur);
        const chk = el.querySelector('.lang-chk');
        if (chk) {
          chk.style.display = isCur ? 'inline' : 'none';
        }
      });
    }

    observeDynamicContent() {
      if (!window.MutationObserver) return;
      let debounceTimer = null;
      const observer = new MutationObserver((mutations) => {
        if (this.isTranslating) return;
        let hasRelevantChange = false;
        for (const m of mutations) {
          if (m.type === 'childList' && m.addedNodes.length > 0) {
            hasRelevantChange = true;
            break;
          }
        }
        if (hasRelevantChange) {
          clearTimeout(debounceTimer);
          debounceTimer = setTimeout(() => {
            this.translateFullDOM();
          }, 60);
        }
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true
      });
    }

    init() {
      const run = () => {
        this.translateFullDOM();
        this.updateLanguagePickers();
        this.observeDynamicContent();
      };

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', run);
      } else {
        run();
      }
    }
  }

  // Initialise global instance
  window.devforgeI18n = new DevForgeI18n();

})();

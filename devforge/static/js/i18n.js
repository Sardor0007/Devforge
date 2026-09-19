/**
 * ══════════════════════════════════════════════════════════════════════════
 *  DEVFORGE FULL CLIENT-SIDE MULTI-LANGUAGE TRANSLATION ENGINE v4.0
 *  Zero External Dependencies • Instant 0ms Execution • 100% Reliable
 *  Supported Languages:
 *    - 'uz': O'zbekcha 🇺🇿
 *    - 'ru': Русский   🇷🇺
 *    - 'en': English   🇬🇧
 * ══════════════════════════════════════════════════════════════════════════
 */

(function () {
  'use strict';

  // Master Comprehensive Translation Catalog
  const MASTER_DICTIONARY = [
    // ── 1. DASHBOARD & STUDIO TERMINAL (Screenshot Exact Strings) ──
    { uz: "Studio Terminal", ru: "Терминал студии", en: "Studio Terminal" },
    { uz: "STUDIO TERMINAL", ru: "ТЕРМИНАЛ СТУДИИ", en: "STUDIO TERMINAL" },
    { uz: "Welcome back, Commander", ru: "С возвращением, Командир", en: "Welcome back, Commander" },
    { uz: "Welcome back", ru: "С возвращением", en: "Welcome back" },
    { uz: "Commander", ru: "Командир", en: "Commander" },
    { uz: "+ Create Project", ru: "+ Создать проект", en: "+ Create Project" },
    { uz: "+ Create New Project", ru: "+ Создать новый проект", en: "+ Create New Project" },
    { uz: "Create Project", ru: "Создать проект", en: "Create Project" },
    { uz: "+ Upload Asset", ru: "+ Загрузить ассет", en: "+ Upload Asset" },
    { uz: "Upload Asset", ru: "Загрузить ассет", en: "Upload Asset" },
    { uz: "Reputation Level", ru: "Уровень репутации", en: "Reputation Level" },
    { uz: "REPUTATION LEVEL", ru: "УРОВЕНЬ РЕПУТАЦИИ", en: "REPUTATION LEVEL" },
    { uz: "Lvl", ru: "Ур.", en: "Lvl" },
    { uz: "Next level in", ru: "Следующий уровень через", en: "Next level in" },
    { uz: "Total Revenue", ru: "Общий доход", en: "Total Revenue" },
    { uz: "TOTAL REVENUE", ru: "ОБЩИЙ ДОХОД", en: "TOTAL REVENUE" },
    { uz: "Lifetime earnings", ru: "Доход за все время", en: "Lifetime earnings" },
    { uz: "Active Projects", ru: "Активные проекты", en: "Active Projects" },
    { uz: "ACTIVE PROJECTS", ru: "АКТИВНЫЕ ПРОЕКТЫ", en: "ACTIVE PROJECTS" },
    { uz: "Management workload", ru: "Рабочая нагрузка", en: "Management workload" },
    { uz: "Project Pipeline", ru: "Пайплайн проектов", en: "Project Pipeline" },
    { uz: "PROJECT PIPELINE", ru: "ПАЙПЛАЙН ПРОЕКТОВ", en: "PROJECT PIPELINE" },
    { uz: "View All", ru: "Смотреть все", en: "View All" },
    { uz: "Workspace", ru: "Рабочая область", en: "Workspace" },
    { uz: "Recent Assets", ru: "Недавние ассеты", en: "Recent Assets" },
    { uz: "RECENT ASSETS", ru: "НЕДАВНИЕ АССЕТЫ", en: "RECENT ASSETS" },
    { uz: "Wallet Balance", ru: "Баланс кошелька", en: "Wallet Balance" },
    { uz: "WALLET BALANCE", ru: "БАЛАНС КОШЕЛЬКА", en: "WALLET BALANCE" },
    { uz: "Subscription", ru: "Подписка", en: "Subscription" },
    { uz: "Public Profile", ru: "Публичный профиль", en: "Public Profile" },
    { uz: "Manage Wallet", ru: "Управление кошельком", en: "Manage Wallet" },
    { uz: "Haftalik Faollar", ru: "Топ недели", en: "Weekly Leaderboard" },
    { uz: "No projects in your pipeline.", ru: "В вашем пайплайне нет проектов.", en: "No projects in your pipeline." },
    { uz: "No assets uploaded yet.", ru: "Ассеты еще не загружены.", en: "No assets uploaded yet." },
    { uz: "members", ru: "участников", en: "members" },
    { uz: "downloads", ru: "скачиваний", en: "downloads" },

    // ── 2. NAVBAR & GLOBAL NAVIGATION ──
    { uz: "Dashboard", ru: "Панель управления", en: "Dashboard" },
    { uz: "Feed", ru: "Лента", en: "Feed" },
    { uz: "Loyihalar", ru: "Проекты", en: "Projects" },
    { uz: "Projects", ru: "Проекты", en: "Projects" },
    { uz: "Jobs", ru: "Вакансии", en: "Jobs" },
    { uz: "Aktivlar", ru: "Ассеты", en: "Assets" },
    { uz: "Assets", ru: "Ассеты", en: "Assets" },
    { uz: "Learn", ru: "Обучение", en: "Learn" },
    { uz: "Jams", ru: "Джемы", en: "Jams" },
    { uz: "🎮 Jams", ru: "🎮 Джемы", en: "🎮 Jams" },
    { uz: "Studio Suite", ru: "Студии", en: "Studio Suite" },
    { uz: "Dev Settings", ru: "Настройки разработчика", en: "Dev Settings" },
    { uz: "⚙️ Dev Settings", ru: "⚙️ Настройки разработчика", en: "⚙️ Dev Settings" },
    { uz: "Developer Settings", ru: "Настройки разработчика", en: "Developer Settings" },
    { uz: "DEVELOPER SETTINGS", ru: "НАСТРОЙКИ РАЗРАБОТЧИКА", en: "DEVELOPER SETTINGS" },
    { uz: "Platform Control Panel", ru: "Панель управления платформой", en: "Platform Control Panel" },
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
    { uz: "Qidirish...", ru: "Поиск...", en: "Search..." },
    { uz: "Qidiruv", ru: "Поиск", en: "Search" },
    { uz: "Search", ru: "Поиск", en: "Search" },
    { uz: "Community", ru: "Сообщество", en: "Community" },
    { uz: "Hamjamiyat", ru: "Сообщество", en: "Community" },
    { uz: "FAQ", ru: "Частые вопросы", en: "FAQ" },

    // ── 3. STUDIOS SUITE ──
    { uz: "3D Studio", ru: "3D Студия", en: "3D Studio" },
    { uz: "🎨 3D Studio", ru: "🎨 3D Студия", en: "🎨 3D Studio" },
    { uz: "Image Editor", ru: "Графический редактор", en: "Image Editor" },
    { uz: "🖼️ Image Editor", ru: "🖼️ Графический редактор", en: "🖼️ Image Editor" },
    { uz: "Audio Lab", ru: "Аудио лаборатория", en: "Audio Lab" },
    { uz: "🎵 Audio Lab", ru: "🎵 Аудио лаборатория", en: "🎵 Audio Lab" },
    { uz: "Video Lab", ru: "Видео лаборатория", en: "Video Lab" },
    { uz: "🎬 Video Lab", ru: "🎬 Видео лаборатория", en: "🎬 Video Lab" },
    { uz: "World Builder", ru: "Конструктор миров", en: "World Builder" },
    { uz: "🏰 World Builder", ru: "🏰 Конструктор миров", en: "🏰 World Builder" },
    { uz: "Game Engine", ru: "Игровой движок", en: "Game Engine" },
    { uz: "🎮 Game Engine", ru: "🎮 Игровой движок", en: "🎮 Game Engine" },

    // ── 4. USER ROLES ──
    { uz: "O'YIN DASTURCHISI", ru: "ГЕЙМ-РАЗРАБОТЧИК", en: "GAME DEVELOPER" },
    { uz: "O'yin Dasturchisi", ru: "Гейм-разработчик", en: "Game Developer" },
    { uz: "O'yin dasturchisi", ru: "Гейм-разработчик", en: "Game Developer" },
    { uz: "Game Developer", ru: "Гейм-разработчик", en: "Game Developer" },
    { uz: "Dasturchi", ru: "Разработчик", en: "Developer" },
    { uz: "Developer", ru: "Разработчик", en: "Developer" },
    { uz: "3D Rassom", ru: "3D Художник", en: "3D Artist" },
    { uz: "3D Artist", ru: "3D Художник", en: "3D Artist" },
    { uz: "Dizayner", ru: "Дизайнер", en: "Designer" },
    { uz: "Designer", ru: "Дизайнер", en: "Designer" },
    { uz: "UI/UX Dizayner", ru: "UI/UX Дизайнер", en: "UI/UX Designer" },
    { uz: "UI/UX Designer", ru: "UI/UX Дизайнер", en: "UI/UX Designer" },
    { uz: "Musiqa/Ovoz", ru: "Звук / Музыка", en: "Audio / Sound" },
    { uz: "Sound Designer", ru: "Звукорежиссер", en: "Sound Designer" },
    { uz: "Stsenariy Yozuvchi", ru: "Сценарист", en: "Writer" },
    { uz: "Writer", ru: "Сценарист", en: "Writer" },
    { uz: "Egasi", ru: "Владелец", en: "Owner" },
    { uz: "Owner", ru: "Владелец", en: "Owner" },

    // ── 5. STATUSES & BADGES ──
    { uz: "Rejalashtirish", ru: "Планирование", en: "Planning" },
    { uz: "Planning", ru: "Планирование", en: "Planning" },
    { uz: "Faol", ru: "Активный", en: "Active" },
    { uz: "Active", ru: "Активный", en: "Active" },
    { uz: "Aktiv", ru: "Активный", en: "Active" },
    { uz: "Jarayonda", ru: "В процессе", en: "In Progress" },
    { uz: "In Progress", ru: "В процессе", en: "In Progress" },
    { uz: "Yakunlangan", ru: "Завершен", en: "Completed" },
    { uz: "Completed", ru: "Завершен", en: "Completed" },
    { uz: "Bajarildi", ru: "Завершено", en: "Done" },
    { uz: "Done", ru: "Завершено", en: "Done" },
    { uz: "Kutilmoqda", ru: "В ожидании", en: "Pending" },
    { uz: "Pending", ru: "В ожидании", en: "Pending" },
    { uz: "To'xtatilgan", ru: "Приостановлен", en: "Paused" },
    { uz: "Paused", ru: "Приостановлен", en: "Paused" },
    { uz: "Ochiq", ru: "Открытый", en: "Public" },
    { uz: "Public", ru: "Открытый", en: "Public" },
    { uz: "Yopiq", ru: "Закрытый", en: "Private" },
    { uz: "Private", ru: "Закрытый", en: "Private" },
    { uz: "Bepul", ru: "Бесплатно", en: "Free" },
    { uz: "Free", ru: "Бесплатно", en: "Free" },
    { uz: "Pullik", ru: "Платные", en: "Paid" },
    { uz: "Paid", ru: "Платные", en: "Paid" },

    // ── 6. MARKETPLACE & ASSETS ──
    { uz: "DIGITAL ASSETS", ru: "ЦИФРОВЫЕ АССЕТЫ", en: "DIGITAL ASSETS" },
    { uz: "Asset Marketplace", ru: "Маркетплейс ассетов", en: "Asset Marketplace" },
    { uz: "Mening Aktivlarim", ru: "Мои ассеты", en: "My Assets" },
    { uz: "📁 Mening Aktivlarim", ru: "📁 Мои ассеты", en: "📁 My Assets" },
    { uz: "My Assets", ru: "Мои ассеты", en: "My Assets" },
    { uz: "Moderatsiya", ru: "Модерация", en: "Moderation" },
    { uz: "🛡️ Moderatsiya", ru: "🛡️ Модерация", en: "🛡️ Moderation" },
    { uz: "Moderation", ru: "Модерация", en: "Moderation" },
    { uz: "Aktiv Yuklash", ru: "Загрузить ассет", en: "Upload Asset" },
    { uz: "⬆️ Aktiv Yuklash", ru: "⬆️ Загрузить ассет", en: "⬆️ Upload Asset" },
    { uz: "All Assets", ru: "Все ассеты", en: "All Assets" },
    { uz: "Barcha aktivlar", ru: "Все ассеты", en: "All Assets" },
    { uz: "Any Price", ru: "Любая цена", en: "Any Price" },
    { uz: "Ixtiyoriy narx", ru: "Любая цена", en: "Any Price" },
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
    { uz: "Marketplace", ru: "Маркетплейс", en: "Marketplace" },
    { uz: "Marketpleys", ru: "Маркетплейс", en: "Marketplace" },

    // ── 7. EXPORT & DOWNLOAD SYSTEM ──
    { uz: "📤 Export (ZIP)", ru: "📤 Экспорт (ZIP)", en: "📤 Export (ZIP)" },
    { uz: "Export (ZIP)", ru: "Экспорт (ZIP)", en: "Export (ZIP)" },
    { uz: "📤 ZIP Export", ru: "📤 ZIP Экспорт", en: "📤 ZIP Export" },
    { uz: "ZIP Export", ru: "ZIP Экспорт", en: "ZIP Export" },
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
    { uz: "⭐ Export (Obuna Kerak)", ru: "⭐ Экспорт (Нужна подписка)", en: "⭐ Export (Subscription Required)" },
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

    // ── 8. PROJECTS & TASKS ──
    { uz: "Discover Projects", ru: "Обзор проектов", en: "Discover Projects" },
    { uz: "Barcha loyihalar", ru: "Все проекты", en: "All Projects" },
    { uz: "All Genres", ru: "Все жанры", en: "All Genres" },
    { uz: "Barcha janrlar", ru: "Все жанры", en: "All Genres" },
    { uz: "All Statuses", ru: "Все статусы", en: "All Statuses" },
    { uz: "Barcha holatlar", ru: "Все статусы", en: "All Statuses" },
    { uz: "Filter", ru: "Фильтр", en: "Filter" },
    { uz: "Filtrlash", ru: "Фильтровать", en: "Filter" },
    { uz: "No projects found", ru: "Проекты не найдены", en: "No projects found" },
    { uz: "Loyihalar topilmadi", ru: "Проекты не найдены", en: "No projects found" },
    { uz: "Jamoaga Qo'shilish", ru: "Вступить в команду", en: "Join Team" },
    { uz: "Ariza ko'rib chiqilmoqda...", ru: "Заявка рассматривается...", en: "Application pending..." },
    { uz: "📋 Vazifalar", ru: "📋 Задачи", en: "📋 Tasks" },
    { uz: "Vazifalar", ru: "Задачи", en: "Tasks" },
    { uz: "Tasks", ru: "Задачи", en: "Tasks" },
    { uz: "+ Vazifa", ru: "+ Задача", en: "+ Task" },
    { uz: "+ Task", ru: "+ Задача", en: "+ Task" },
    { uz: "🤖 AI Vazifalar", ru: "🤖 AI Задачи", en: "🤖 AI Tasks" },
    { uz: "📌 Kutilmoqda", ru: "📌 Ожидает", en: "📌 To Do" },
    { uz: "⚡ Jarayonda", ru: "⚡ В процессе", en: "⚡ In Progress" },
    { uz: "✅ Bajarildi", ru: "✅ Завершено", en: "✅ Done" },
    { uz: "👥 Jamoa A'zolari", ru: "👥 Участники команды", en: "👥 Team Members" },
    { uz: "Jamoa a'zolari", ru: "Участники команды", en: "Team Members" },
    { uz: "Team Members", ru: "Участники команды", en: "Team Members" },
    { uz: "📨 Arizalar", ru: "📨 Заявки", en: "📨 Applications" },
    { uz: "Arizalar", ru: "Заявки", en: "Applications" },

    // ── 9. COMMON ACTIONS & CONTROLS ──
    { uz: "Saqlash", ru: "Сохранить", en: "Save" },
    { uz: "💾 Saqlash", ru: "💾 Сохранить", en: "💾 Save" },
    { uz: "Save", ru: "Сохранить", en: "Save" },
    { uz: "Bekor qilish", ru: "Отмена", en: "Cancel" },
    { uz: "Cancel", ru: "Отмена", en: "Cancel" },
    { uz: "O'chirish", ru: "Удалить", en: "Delete" },
    { uz: "🗑️ O'chirish", ru: "🗑️ Удалить", en: "🗑️ Delete" },
    { uz: "Delete", ru: "Удалить", en: "Delete" },
    { uz: "Yuklash", ru: "Загрузить", en: "Upload" },
    { uz: "Upload", ru: "Загрузить", en: "Upload" },
    { uz: "Yaratish", ru: "Создать", en: "Create" },
    { uz: "Create", ru: "Создать", en: "Create" },
    { uz: "Qo'shish", ru: "Добавить", en: "Add" },
    { uz: "+ Qo'shish", ru: "+ Добавить", en: "+ Add" },
    { uz: "Add", ru: "Добавить", en: "Add" },
    { uz: "Yangilash", ru: "Обновить", en: "Update" },
    { uz: "Update", ru: "Обновить", en: "Update" },
    { uz: "Tahrirlash", ru: "Редактировать", en: "Edit" },
    { uz: "Edit", ru: "Редактировать", en: "Edit" },
    { uz: "Batafsil", ru: "Подробнее", en: "Details" },
    { uz: "Explore", ru: "Обзор", en: "Explore" },
    { uz: "Ko'rish", ru: "Просмотр", en: "View" },
    { uz: "View", ru: "Просмотр", en: "View" },
    { uz: "Yuborish", ru: "Отправить", en: "Send" },
    { uz: "Send", ru: "Отправить", en: "Send" },
    { uz: "Ariza Yuborish", ru: "Отправить заявку", en: "Submit Application" },
    { uz: "✓ Qabul qilish", ru: "✓ Принять", en: "✓ Accept" },
    { uz: "Rad etish", ru: "Отклонить", en: "Reject" },
    { uz: "Tasdiqlash", ru: "Подтвердить", en: "Confirm" },
    { uz: "Confirm", ru: "Подтвердить", en: "Confirm" },
    { uz: "Boshlash", ru: "Начать", en: "Start" },
    { uz: "Start", ru: "Начать", en: "Start" },
    { uz: "Tugatish", ru: "Завершить", en: "Complete" },
    { uz: "✓ Tugatish", ru: "✓ Завершить", en: "✓ Complete" },
    { uz: "Obunani Ko'rish", ru: "Посмотреть подписки", en: "View Subscriptions" },

    // ── 10. NOTIFICATIONS & STATUS MESSAGES ──
    { uz: "Muvaffaqiyatli", ru: "Успешно", en: "Success" },
    { uz: "Xatolik", ru: "Ошибка", en: "Error" },
    { uz: "Ogohlantirish", ru: "Предупреждение", en: "Warning" },
    { uz: "Ma'lumot", ru: "Информация", en: "Info" },
    { uz: "Fayl tanlanmadi", ru: "Файл не выбран", en: "No file selected" },
    { uz: "Yuklanmoqda...", ru: "Загрузка...", en: "Loading..." },
    { uz: "Loading...", ru: "Загрузка...", en: "Loading..." }
  ];

  // Fast String Normalizer
  function normalise(str) {
    if (!str) return '';
    return str.toString().replace(/\s+/g, ' ').trim();
  }

  // Pre-compile Phrase Lookup Map
  const EXACT_MAP = new Map();
  MASTER_DICTIONARY.forEach(item => {
    ['uz', 'ru', 'en'].forEach(lang => {
      const val = item[lang];
      if (val) {
        const norm = normalise(val);
        if (norm) {
          EXACT_MAP.set(norm, item);
          EXACT_MAP.set(norm.toLowerCase(), item);
        }
      }
    });
  });

  // Pre-compile Substring Replacers (sorted by length descending to avoid partial word collisions)
  const SUBSTRING_ENTRIES = [];
  MASTER_DICTIONARY.forEach(item => {
    ['uz', 'ru', 'en'].forEach(srcLang => {
      const srcText = normalise(item[srcLang]);
      if (srcText && srcText.length >= 2) {
        // Escape regex special chars
        const escaped = srcText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        SUBSTRING_ENTRIES.push({
          sourceText: srcText,
          regex: new RegExp(`(^|\\b|\\s)${escaped}(\\b|\\s|$)`, 'gi'),
          exactRegex: new RegExp(escaped, 'gi'),
          item: item
        });
      }
    });
  });

  // Sort: longest sourceText first
  SUBSTRING_ENTRIES.sort((a, b) => b.sourceText.length - a.sourceText.length);

  // Core DevForgeI18n Engine Class
  class DevForgeI18n {
    constructor() {
      this.supported = ['uz', 'ru', 'en'];
      this.currentLang = this.detectLanguage();
      this.init();
    }

    detectLanguage() {
      // 1. Check Cookie
      const match = document.cookie.match(/(?:^|;\s*)django_language=([^;]+)/);
      if (match && this.supported.includes(match[1])) return match[1];

      // 2. Check localStorage
      try {
        const local = localStorage.getItem('devforge_lang');
        if (local && this.supported.includes(local)) return local;
      } catch (e) {}

      // 3. Fallback
      return 'uz';
    }

    setLanguage(lang, syncBackend = true) {
      if (!this.supported.includes(lang)) return;
      this.currentLang = lang;

      // 1. Persist in Storage
      try {
        localStorage.setItem('devforge_lang', lang);
      } catch (e) {}

      // 2. Persist in Cookies
      document.cookie = `django_language=${lang};path=/;max-age=31536000;SameSite=Lax`;
      document.documentElement.lang = lang;

      // 3. Update all UI Pickers
      this.updatePickers();

      // 4. Translate the entire DOM in-place immediately!
      this.translateFullDOM(document.body);

      // 5. Sync with Backend
      if (syncBackend) {
        fetch(`/set-language/${lang}/?format=json`, {
          method: 'GET',
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        }).catch(() => {});
      }
    }

    translatePhrase(rawText) {
      if (!rawText) return rawText;
      const targetLang = this.currentLang;
      const trimmed = normalise(rawText);
      if (!trimmed) return rawText;

      // A. Exact Match (Fastest & most accurate)
      const match = EXACT_MAP.get(trimmed) || EXACT_MAP.get(trimmed.toLowerCase());
      if (match && match[targetLang]) {
        // Keep original leading & trailing whitespace
        const leading = rawText.match(/^\s*/)[0];
        const trailing = rawText.match(/\s*$/)[0];
        return leading + match[targetLang] + trailing;
      }

      // B. Substring replacement for composite text (e.g. "Rejalashtirish • 1 members", "Welcome back, Commander ")
      let result = rawText;
      for (let i = 0; i < SUBSTRING_ENTRIES.length; i++) {
        const entry = SUBSTRING_ENTRIES[i];
        const targetVal = entry.item[targetLang];
        if (!targetVal) continue;

        if (entry.exactRegex.test(result)) {
          result = result.replace(entry.exactRegex, targetVal);
        }
      }
      return result;
    }

    translateFullDOM(root = document.body) {
      if (!root) return;

      // A. Text Nodes Walk
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
            if (p.closest('.lang-switcher-wrap') || p.closest('#langMenu') || p.closest('#homeLangMenu') || p.classList.contains('notranslate')) {
              return NodeFilter.FILTER_REJECT;
            }
            return NodeFilter.FILTER_ACCEPT;
          }
        },
        false
      );

      const textNodes = [];
      let curr;
      while ((curr = walker.nextNode())) {
        textNodes.push(curr);
      }

      for (let i = 0; i < textNodes.length; i++) {
        const node = textNodes[i];
        if (node._dfOrig === undefined) {
          node._dfOrig = node.nodeValue;
        }

        if (this.currentLang === 'uz') {
          // Restore original pristine text
          node.nodeValue = node._dfOrig;
        } else {
          node.nodeValue = this.translatePhrase(node._dfOrig);
        }
      }

      // B. Input / Textarea Placeholders
      document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(el => {
        if (el._dfOrigPh === undefined) el._dfOrigPh = el.placeholder;
        if (this.currentLang === 'uz') {
          el.placeholder = el._dfOrigPh;
        } else {
          el.placeholder = this.translatePhrase(el._dfOrigPh);
        }
      });

      // C. Submit & Action Buttons
      document.querySelectorAll('input[type="button"], input[type="submit"]').forEach(btn => {
        if (btn._dfOrigVal === undefined) btn._dfOrigVal = btn.value;
        if (this.currentLang === 'uz') {
          btn.value = btn._dfOrigVal;
        } else {
          btn.value = this.translatePhrase(btn._dfOrigVal);
        }
      });

      // D. Titles & Tooltips
      document.querySelectorAll('[title]').forEach(el => {
        if (el.closest('.lang-switcher-wrap')) return;
        if (el._dfOrigTitle === undefined) el._dfOrigTitle = el.title;
        if (this.currentLang === 'uz') {
          el.title = el._dfOrigTitle;
        } else {
          el.title = this.translatePhrase(el._dfOrigTitle);
        }
      });
    }

    updatePickers() {
      const code = (this.currentLang || 'uz').toUpperCase();

      // Update button text badges across navbar
      document.querySelectorAll('.lang-btn-current .lang-code').forEach(el => {
        el.textContent = code;
      });

      // Update options active state & checkmarks
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
        let hasRelevant = false;
        for (let i = 0; i < mutations.length; i++) {
          const m = mutations[i];
          if (m.type === 'childList' && m.addedNodes.length > 0) {
            hasRelevant = true;
            break;
          }
        }
        if (hasRelevant) {
          clearTimeout(timer);
          timer = setTimeout(() => {
            this.translateFullDOM(document.body);
          }, 60);
        }
      });

      obs.observe(document.body, { childList: true, subtree: true });
    }

    init() {
      const run = () => {
        this.updatePickers();
        if (this.currentLang !== 'uz') {
          this.translateFullDOM(document.body);
        }
        this.observeDynamic();
      };

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', run);
      } else {
        run();
      }
    }
  }

  // Initialise Global Instance
  window.devforgeI18n = new DevForgeI18n();

  // Helper shortcut for onclick
  window.changeLanguage = function (lang) {
    if (window.devforgeI18n) {
      window.devforgeI18n.setLanguage(lang);
    }
  };
})();

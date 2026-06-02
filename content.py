"""Схема и значения по умолчанию для всего редактируемого контента сайта.

SETTINGS_SCHEMA описывает каждое скалярное поле: группу, подпись и тип
(`text`, `textarea`, `url`). Админ-форма генерируется автоматически из этой схемы,
поэтому, чтобы добавить новое редактируемое поле, достаточно вписать его сюда.
"""

# group -> человекочитаемое название группы (порядок задаёт порядок в админке)
GROUPS = {
    "general": "Общее",
    "intro":   "Заставка (печатающийся текст)",
    "hero":    "Главный экран",
    "about":   "Обо мне",
    "contact": "Контакты",
}

# key -> (group, label, type, default)
SETTINGS_SCHEMA = {
    # ── Общее ────────────────────────────────────────────
    "logo":          ("general", "Логотип / название", "text", "amalproj"),
    "marquee":       ("general", "Бегущая строка (через запятую)", "textarea",
                      "Python, FastAPI, React, TypeScript, PostgreSQL, Docker, Claude API, Redis, AWS, WebSockets"),
    "footer_left":   ("general", "Подвал — слева", "text", "© 2026 amalproj"),
    "footer_right":  ("general", "Подвал — справа", "text", "Built with FastAPI · Python"),

    # ── Заставка ─────────────────────────────────────────
    "intro_greeting": ("intro", "Приветствие", "text", "Привет, я "),
    "intro_name":     ("intro", "Имя (выделено синим)", "text", "Амаль"),
    "intro_middle":   ("intro", "Текст между", "text", ", учусь на специальности "),
    "intro_specialty":("intro", "Специальность (выделено синим)", "text", "«Торговое дело»"),

    # ── Главный экран ────────────────────────────────────
    "hero_eyebrow":  ("hero", "Надзаголовок", "text", "Full-Stack Developer · 2026"),
    "hero_line1":    ("hero", "Заголовок — строка 1", "text", "Создаю"),
    "hero_line2":    ("hero", "Заголовок — строка 2 (синяя)", "text", "цифровые"),
    "hero_line3":    ("hero", "Заголовок — строка 3", "text", "продукты"),
    "hero_desc":     ("hero", "Описание под заголовком", "textarea",
                      "Превращаю идеи в работающий код.\nМинимализм, производительность, детали."),
    "hero_btn":      ("hero", "Текст кнопки", "text", "Смотреть работы"),
    "scroll_text":   ("hero", "Подсказка прокрутки", "text", "Листайте вниз"),

    # ── Обо мне ──────────────────────────────────────────
    "about_label":   ("about", "Метка секции", "text", "01 — Обо мне"),
    "about_number":  ("about", "Большая цифра", "text", "05"),
    "about_heading": ("about", "Заголовок", "text", "Разработчик, влюблённый в детали."),
    "about_p1":      ("about", "Абзац 1", "textarea",
                      "5 лет создаю веб-приложения — от быстрых API на Python до интерактивных интерфейсов на React. Верю, что хороший код читается как хорошая проза."),
    "about_p2":      ("about", "Абзац 2", "textarea",
                      "Работаю с AI-инструментами нового поколения, строю production-ready системы и постоянно нахожу что-то новое для изучения."),
    "stat1_value":   ("about", "Стат. 1 — число", "text", "5"),
    "stat1_suffix":  ("about", "Стат. 1 — суффикс", "text", "+"),
    "stat1_label":   ("about", "Стат. 1 — подпись", "text", "Лет опыта"),
    "stat2_value":   ("about", "Стат. 2 — число", "text", "40"),
    "stat2_suffix":  ("about", "Стат. 2 — суффикс", "text", "+"),
    "stat2_label":   ("about", "Стат. 2 — подпись", "text", "Проектов"),
    "stat3_value":   ("about", "Стат. 3 — число", "text", "99"),
    "stat3_suffix":  ("about", "Стат. 3 — суффикс", "text", "%"),
    "stat3_label":   ("about", "Стат. 3 — подпись", "text", "Довольных"),

    # ── Контакты ─────────────────────────────────────────
    "contact_label": ("contact", "Метка секции", "text", "04 — Контакт"),
    "contact_line1": ("contact", "Заголовок — строка 1", "text", "Давай"),
    "contact_line2": ("contact", "Заголовок — строка 2", "text", "работать"),
    "contact_line3": ("contact", "Заголовок — строка 3 (синяя)", "text", "вместе"),
    "contact_email": ("contact", "Email", "text", "hello@alexdev.io"),
    "social_github":   ("contact", "GitHub (ссылка)", "url", "#"),
    "social_linkedin": ("contact", "LinkedIn (ссылка)", "url", "#"),
    "social_telegram": ("contact", "Telegram (ссылка)", "url", "#"),
    "social_twitter":  ("contact", "Twitter (ссылка)", "url", "#"),
}

# Проекты и навыки по умолчанию (для первичного заполнения базы)
DEFAULT_PROJECTS = [
    {"num": "001", "icon": "🛒", "title": "E-Commerce Platform",
     "description": "Маркетплейс с оплатой, корзиной, личным кабинетом и аналитикой продаж.",
     "link": "#"},
    {"num": "002", "icon": "🤖", "title": "AI Chat Assistant",
     "description": "Мультимодальный чат-бот с памятью, поддержкой файлов и стриминговым ответом.",
     "link": "#"},
    {"num": "003", "icon": "📊", "title": "Analytics Dashboard",
     "description": "Дашборд реального времени с WebSocket-потоком, фильтрами и экспортом.",
     "link": "#"},
]

DEFAULT_SKILLS = [
    {"idx": "01", "name": "Python / FastAPI",    "tags": "async, REST, Pydantic"},
    {"idx": "02", "name": "React / TypeScript",  "tags": "SPA, Zustand, Tailwind"},
    {"idx": "03", "name": "Базы данных",          "tags": "PostgreSQL, Redis, MongoDB"},
    {"idx": "04", "name": "DevOps / Cloud",       "tags": "Docker, CI/CD, AWS"},
    {"idx": "05", "name": "AI / LLM",             "tags": "Claude API, LangChain, RAG"},
]


def default_settings() -> dict:
    """Словарь key -> значение по умолчанию."""
    return {key: meta[3] for key, meta in SETTINGS_SCHEMA.items()}

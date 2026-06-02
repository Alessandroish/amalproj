# amalproj — сайт-портфолио

Лендинг на FastAPI с анимациями и **админ-панелью** для управления всем контентом.

- Публичный сайт: `/`
- Админка: `/admin/login` (вход по логину + паролю + PIN)

---

## Локальный запуск

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Сайт: http://localhost:8000 · Админка: http://localhost:8000/admin/login
Данные по умолчанию: `admin` / `admin123` / PIN `1234` (поменяйте через переменные окружения).

---

## Структура проекта

| Файл / папка            | Назначение                                   |
|-------------------------|----------------------------------------------|
| `main.py`               | FastAPI: сайт, админка, приём заявок          |
| `db.py`                 | База данных SQLite (контент, проекты, заявки) |
| `content.py`            | Схема и значения по умолчанию                 |
| `templates/`            | HTML-шаблоны (сайт + админка)                 |
| `static/`               | CSS, JS                                       |
| `requirements.txt`      | Python-зависимости                            |
| `Procfile`              | Команда запуска для хостинга                  |

---

## Деплой на Railway (по шагам)

### Шаг 1. GitHub
1. Зарегистрируйтесь на https://github.com
2. Создайте новый репозиторий (кнопка **New**), назовите, например, `amalproj`, оставьте **пустым** (без README).
3. Загрузите код (команды выполняются в папке проекта):

```bash
git init
git add .
git commit -m "amalproj: сайт + админка"
git branch -M main
git remote add origin https://github.com/ВАШ_ЛОГИН/amalproj.git
git push -u origin main
```

> При `push` GitHub попросит логин и **токен** (не пароль). Токен создаётся тут:
> Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate,
> отметьте галочку `repo`. Скопируйте токен и вставьте вместо пароля.

### Шаг 2. Railway
1. Зайдите на https://railway.app → **Login with GitHub**.
2. **New Project → Deploy from GitHub repo** → выберите `amalproj`.
3. Railway сам определит Python, поставит зависимости и запустит по `Procfile`.

### Шаг 3. Секреты (Variables)
В проекте Railway откройте вкладку **Variables** и добавьте:

| Переменная       | Значение                                              |
|------------------|-------------------------------------------------------|
| `SESSION_SECRET` | длинная случайная строка (см. ниже)                   |
| `ADMIN_USER`     | ваш логин                                             |
| `ADMIN_PASSWORD` | надёжный пароль                                       |
| `ADMIN_PIN`      | ваш PIN                                               |
| `DB_PATH`        | `/data/site.db`                                       |

Сгенерировать `SESSION_SECRET`:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Шаг 4. Постоянное хранилище (важно!)
SQLite-база должна жить на постоянном диске, иначе данные сбросятся при обновлении.
1. В сервисе: **Settings → Volumes → Add Volume**, путь монтирования: `/data`.
2. Убедитесь, что `DB_PATH=/data/site.db` (из шага 3).

### Шаг 5. Открыть сайт
**Settings → Networking → Generate Domain** — получите адрес вида
`amalproj-production.up.railway.app`. Сайт в сети!

---

## Подключение своего домена

1. Купите домен (reg.ru, Cloudflare и т.п.).
2. В Railway: **Settings → Networking → Custom Domain** → введите домен.
3. Railway покажет CNAME-запись — добавьте её в DNS-настройках домена у регистратора.
4. Через несколько минут (до пары часов) домен заработает с HTTPS автоматически.

---

## Обновление сайта после деплоя

Любая правка кода → снова на GitHub, Railway пересоберёт автоматически:

```bash
git add .
git commit -m "что изменил"
git push
```

Контент (тексты, проекты, заявки) меняется **без кода** — через админку `/admin`.

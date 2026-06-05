"""FastAPI-приложение: публичный сайт + защищённая админ-панель.

Запуск:  python3 -m uvicorn main:app --reload
Вход в админку:  /admin/login
"""
from __future__ import annotations

import hmac
import os

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import content
import db

# ── конфигурация / секреты (берутся из окружения, есть значения по умолчанию) ──
SESSION_SECRET = os.environ.get("SESSION_SECRET", "change-me-in-production-please")
ADMIN_USER     = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
ADMIN_PIN      = os.environ.get("ADMIN_PIN", "1234")


def _same(a: str, b: str) -> bool:
    """Сравнение строк за константное время (защита от тайминг-атак)."""
    return hmac.compare_digest(a.encode(), b.encode())

app = FastAPI(title="amalproj")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, max_age=60 * 60 * 24 * 7)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def _startup() -> None:
    db.init_db()


def is_authed(request: Request) -> bool:
    return bool(request.session.get("auth"))


def require_auth(request: Request):
    """Возвращает RedirectResponse на логин, если пользователь не авторизован."""
    if not is_authed(request):
        return RedirectResponse("/admin/login", status_code=303)
    return None


# ═══════════════════════════════════════════════════════════
#  ПУБЛИЧНЫЙ САЙТ
# ═══════════════════════════════════════════════════════════
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    with db.SessionLocal() as s:
        ctx = {
            "request":  request,
            "s":        db.get_settings(s),
            "projects": db.get_projects(s),
            "skills":   [
                {"idx": sk.idx, "name": sk.name,
                 "tags": [t.strip() for t in sk.tags.split(",") if t.strip()]}
                for sk in db.get_skills(s)
            ],
            "marquee":  [m.strip() for m in
                         db.get_settings(s).get("marquee", "").split(",") if m.strip()],
        }
    return templates.TemplateResponse("index.html", ctx)


@app.post("/contact")
def contact(name: str = Form(""), email: str = Form(""), body: str = Form("")):
    with db.SessionLocal() as s:
        s.add(db.Message(name=name.strip(), email=email.strip(), body=body.strip()))
        s.commit()
    return RedirectResponse("/?sent=1#contact", status_code=303)


# ═══════════════════════════════════════════════════════════
#  АВТОРИЗАЦИЯ В АДМИНКУ
# ═══════════════════════════════════════════════════════════


@app.get("/admin/login", response_class=HTMLResponse)
def login_form(request: Request, error: str = ""):
    if is_authed(request):
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse("admin/login.html",
                                      {"request": request, "error": error})


@app.post("/admin/login")
def login(request: Request,
          username: str = Form(...), password: str = Form(...), pin: str = Form(...)):
    ok = (_same(username, ADMIN_USER)
          and _same(password, ADMIN_PASSWORD)
          and _same(pin, ADMIN_PIN))
    if not ok:
        return RedirectResponse("/admin/login?error=Неверный+логин,+пароль+или+PIN",
                                status_code=303)
    request.session["auth"] = True
    return RedirectResponse("/admin", status_code=303)


@app.get("/admin/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=303)


# ═══════════════════════════════════════════════════════════
#  АДМИН-ПАНЕЛЬ
# ═══════════════════════════════════════════════════════════
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    if (r := require_auth(request)):
        return r
    with db.SessionLocal() as s:
        unread = sum(1 for m in db.get_messages(s) if not m.is_read)
        counts = {
            "projects": len(db.get_projects(s)),
            "skills":   len(db.get_skills(s)),
            "messages": len(db.get_messages(s)),
            "unread":   unread,
        }
    return templates.TemplateResponse("admin/dashboard.html",
                                      {"request": request, "counts": counts})


# ── Контент (настройки) ──────────────────────────────────
@app.get("/admin/content", response_class=HTMLResponse)
def admin_content(request: Request, saved: int = 0):
    if (r := require_auth(request)):
        return r
    with db.SessionLocal() as s:
        values = db.get_settings(s)
    # сгруппировать поля по разделам для удобной формы
    groups = {gkey: {"title": gtitle, "fields": []}
              for gkey, gtitle in content.GROUPS.items()}
    for key, (gkey, label, ftype, _default) in content.SETTINGS_SCHEMA.items():
        groups[gkey]["fields"].append(
            {"key": key, "label": label, "type": ftype, "value": values.get(key, "")})
    return templates.TemplateResponse(
        "admin/content.html",
        {"request": request, "groups": groups, "saved": saved})


@app.post("/admin/content")
async def admin_content_save(request: Request):
    if (r := require_auth(request)):
        return r
    form = await request.form()
    with db.SessionLocal() as s:
        settings = {row.key: row for row in s.query(db.Setting).all()}
        for key in content.SETTINGS_SCHEMA:
            if key in form:
                if key in settings:
                    settings[key].value = str(form[key])
                else:
                    s.add(db.Setting(key=key, value=str(form[key])))
        s.commit()
    return RedirectResponse("/admin/content?saved=1", status_code=303)


# ── Проекты ──────────────────────────────────────────────
@app.get("/admin/projects", response_class=HTMLResponse)
def admin_projects(request: Request):
    if (r := require_auth(request)):
        return r
    with db.SessionLocal() as s:
        projects = db.get_projects(s)
    return templates.TemplateResponse("admin/projects.html",
                                      {"request": request, "projects": projects})


@app.post("/admin/projects/save")
async def admin_projects_save(request: Request):
    if (r := require_auth(request)):
        return r
    form = await request.form()
    pid = form.get("id")
    with db.SessionLocal() as s:
        if pid:  # редактирование существующего
            p = s.get(db.Project, int(pid))
        else:    # новый — в конец списка
            p = db.Project(sort=len(db.get_projects(s)))
            s.add(p)
        p.num = str(form.get("num", ""))
        p.icon = str(form.get("icon", ""))
        p.title = str(form.get("title", ""))
        p.description = str(form.get("description", ""))
        p.link = str(form.get("link", "#")) or "#"
        s.commit()
    return RedirectResponse("/admin/projects", status_code=303)


@app.post("/admin/projects/delete")
def admin_projects_delete(id: int = Form(...)):
    with db.SessionLocal() as s:
        if (p := s.get(db.Project, id)):
            s.delete(p)
            s.commit()
    return RedirectResponse("/admin/projects", status_code=303)


# ── Навыки ───────────────────────────────────────────────
@app.get("/admin/skills", response_class=HTMLResponse)
def admin_skills(request: Request):
    if (r := require_auth(request)):
        return r
    with db.SessionLocal() as s:
        skills = db.get_skills(s)
    return templates.TemplateResponse("admin/skills.html",
                                      {"request": request, "skills": skills})


@app.post("/admin/skills/save")
async def admin_skills_save(request: Request):
    if (r := require_auth(request)):
        return r
    form = await request.form()
    sid = form.get("id")
    with db.SessionLocal() as s:
        if sid:
            sk = s.get(db.Skill, int(sid))
        else:
            sk = db.Skill(sort=len(db.get_skills(s)))
            s.add(sk)
        sk.idx = str(form.get("idx", ""))
        sk.name = str(form.get("name", ""))
        sk.tags = str(form.get("tags", ""))
        s.commit()
    return RedirectResponse("/admin/skills", status_code=303)


@app.post("/admin/skills/delete")
def admin_skills_delete(id: int = Form(...)):
    with db.SessionLocal() as s:
        if (sk := s.get(db.Skill, id)):
            s.delete(sk)
            s.commit()
    return RedirectResponse("/admin/skills", status_code=303)


# ── Заявки ───────────────────────────────────────────────
@app.get("/admin/messages", response_class=HTMLResponse)
def admin_messages(request: Request):
    if (r := require_auth(request)):
        return r
    with db.SessionLocal() as s:
        messages = db.get_messages(s)
        # пометить все как прочитанные при открытии
        for m in messages:
            m.is_read = True
        s.commit()
        messages = db.get_messages(s)
    return templates.TemplateResponse("admin/messages.html",
                                      {"request": request, "messages": messages})


@app.post("/admin/messages/delete")
def admin_messages_delete(id: int = Form(...)):
    with db.SessionLocal() as s:
        if (m := s.get(db.Message, id)):
            s.delete(m)
            s.commit()
    return RedirectResponse("/admin/messages", status_code=303)

"""Слой базы данных (SQLite через SQLAlchemy).

Таблицы:
  setting  — пары ключ/значение для всех скалярных текстов сайта
  project  — карточки проектов (с порядком сортировки)
  skill    — строки навыков (с порядком сортировки)
  message  — заявки, присланные через форму контактов
"""
from __future__ import annotations

import os
from datetime import datetime

from sqlalchemy import (
    Boolean, DateTime, Integer, String, Text, create_engine, select,
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, sessionmaker,
)

import content

DB_PATH = os.environ.get("DB_PATH", "site.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Setting(Base):
    __tablename__ = "setting"
    key:   Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="")


class Project(Base):
    __tablename__ = "project"
    id:          Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sort:        Mapped[int] = mapped_column(Integer, default=0)
    num:         Mapped[str] = mapped_column(String, default="")
    icon:        Mapped[str] = mapped_column(String, default="")
    title:       Mapped[str] = mapped_column(String, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    link:        Mapped[str] = mapped_column(String, default="#")


class Skill(Base):
    __tablename__ = "skill"
    id:   Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    idx:  Mapped[str] = mapped_column(String, default="")
    name: Mapped[str] = mapped_column(String, default="")
    tags: Mapped[str] = mapped_column(String, default="")  # через запятую


class Message(Base):
    __tablename__ = "message"
    id:         Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:       Mapped[str] = mapped_column(String, default="")
    email:      Mapped[str] = mapped_column(String, default="")
    body:       Mapped[str] = mapped_column(Text, default="")
    is_read:    Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def init_db() -> None:
    """Создать таблицы и при первом запуске залить контент по умолчанию."""
    Base.metadata.create_all(engine)
    with SessionLocal() as s:
        # настройки: добавляем недостающие ключи, не трогая уже изменённые
        existing = {row.key for row in s.scalars(select(Setting)).all()}
        for key, val in content.default_settings().items():
            if key not in existing:
                s.add(Setting(key=key, value=val))

        # проекты/навыки заполняем только если таблицы пусты
        if not s.scalars(select(Project)).first():
            for i, p in enumerate(content.DEFAULT_PROJECTS):
                s.add(Project(sort=i, **p))
        if not s.scalars(select(Skill)).first():
            for i, sk in enumerate(content.DEFAULT_SKILLS):
                s.add(Skill(sort=i, **sk))
        s.commit()


def get_settings(s) -> dict:
    """Все настройки одним словарём key -> value."""
    return {row.key: row.value for row in s.scalars(select(Setting)).all()}


def get_projects(s):
    return s.scalars(select(Project).order_by(Project.sort, Project.id)).all()


def get_skills(s):
    return s.scalars(select(Skill).order_by(Skill.sort, Skill.id)).all()


def get_messages(s):
    return s.scalars(select(Message).order_by(Message.created_at.desc())).all()

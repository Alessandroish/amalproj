#!/usr/bin/env bash
# Локальный запуск одной командой:  ./run.sh
set -e
echo "→ Устанавливаю зависимости..."
pip install -q -r requirements.txt
echo "→ Запускаю сайт на http://localhost:8000  (админка: /admin/login)"
uvicorn main:app --reload

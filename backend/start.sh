#!/bin/sh

# Cloud Run 전용 시작 스크립트
# - DB 마이그레이션: 앱 시작 전 실행 (Alembic — 冪等)
# - Cloud Run은 GCP 네트워크에서 Supabase에 직접 연결 가능
# - GitHub Actions 러너는 IPv6 제약으로 Supabase 직접 연결 불가

set -e

echo "Starting LumiNine backend (Cloud Run mode)..."
echo "PORT: ${PORT:-5001}"

# ── DB 마이그레이션 (Alembic) ──────────────────────────────
# Alembic이 alembic_version 테이블로 적용 여부를 관리하므로 冪等
echo "Running database migrations..."
cd /app && PYTHONPATH=. FLASK_APP=app.py flask db upgrade
echo "Database migrations completed."

# Cloud Run이 주입하는 $PORT를 사용, 없으면 5001 (로컬 개발)
BIND_PORT="${PORT:-5001}"

exec gunicorn \
  --bind "0.0.0.0:${BIND_PORT}" \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  --access-logformat '%(h)s %(l)s %(u)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" forwarded_for="%({X-Forwarded-For}i)s"' \
  --chdir /app \
  --workers 2 \
  --timeout 120 \
  --worker-class sync \
  --preload \
  'app:app'

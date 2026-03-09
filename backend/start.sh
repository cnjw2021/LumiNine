#!/bin/sh

# Cloud Run 전용 시작 스크립트
# - wait_for_db: Cloud Run은 DB에 직접 연결하므로 불필요 (제거)
# - cron/logrotate: Cloud Run은 임시 파일시스템, 로그는 stdout으로 출력 (제거)
# - New Relic: 환경변수 NEW_RELIC_LICENSE_KEY 미설정 시 비활성화

set -e

echo "Starting LumiNine backend (Cloud Run mode)..."
echo "PORT: ${PORT:-5001}"

# Cloud Run이 주입하는 $PORT를 사용, 없으면 5001 (로컬 개발)
BIND_PORT="${PORT:-5001}"

# DB 초기화: テーブル確認 → 不足分DDL+シード → スーパーユーザー作成
# run_init() は冪等 (IF NOT EXISTS / ON CONFLICT) なのでコールドスタート毎に安全に実行可能
echo "Running DB init..."
python -c "from db_manage import run_init; run_init()"
echo "DB init complete."

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

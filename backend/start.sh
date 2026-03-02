#!/bin/sh

# スクリプト実行中にエラーが発生した場合、即座に停止
set -e

echo "Waiting for MySQL to be ready..."
python /app/wait_for_db.py
echo "MySQL is ready!"

echo "Setting up log directories..."
# ボリュームでマウントされる可能性があるため、コンテナ起動時のディレクトリ構造と権限を保証します。
mkdir -p /app/logs/archive/access /app/logs/archive/error /app/logs/archive/app
touch /app/logs/access.log /app/logs/error.log /app/logs/app.log
chmod -R 755 /app/logs
chown -R appuser:appgroup /app/logs

echo "Copying SVG images..."
# /app/frontend_imagesはdocker-composeでマウントしたボリュームです。
mkdir -p /app/apps/ninestarki/static/images/main_star/simple
# cp コマンドに -n (no-clobber) オプションを追加して、上書きしないようにします。
cp -f /app/frontend_images/*.svg /app/apps/ninestarki/static/images/main_star/ 2>/dev/null || true
cp -f /app/frontend_images/simple/*.svg /app/apps/ninestarki/static/images/main_star/simple/ 2>/dev/null || true
echo "SVG images copied."

echo "Initializing database..."
cd /app
python db_manage.py init
echo "Database initialization completed."

echo "Starting cron service..."
service cron start

echo "Forcing logrotate to run once to check status..."
# 初回の state file 作成に root 権限が必要
/usr/sbin/logrotate -f /etc/logrotate.d/gunicorn || true
# logrotate が root で作成したファイルを appuser が書き込めるように再設定
chown -R appuser:appgroup /app/logs

echo "Preparing /tmp/pdf permissions..."
mkdir -p /tmp/pdf
chown -R appuser:appgroup /tmp/pdf || true

echo "Starting gunicorn (as appuser)..."
# exec で PID1 を gunicorn にしつつ、実行ユーザーを appuser へ降格
# New Relic エージェント経由で起動
exec su -s /bin/sh -c "newrelic-admin run-program gunicorn \
  --bind 0.0.0.0:5001 \
  --log-level debug \
  --access-logfile /app/logs/access.log \
  --error-logfile /app/logs/error.log \
  --capture-output \
  --access-logformat '%(h)s %(l)s %(u)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\" forwarded_for=\"%({X-Forwarded-For}i)s\"' \
  --chdir /app \
  --workers 2 \
  --timeout 120 \
  --worker-class sync \
  --preload \
  'app:app'" appuser


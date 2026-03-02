# Docker 스택 가이드 (운영/개발, Nginx, Worker, Makefile)

본 문서는 운영/개발 환경에서 동일하게 재현 가능한 Docker 스택 구성을 정리합니다.

## 1) 운영 docker-compose.yml 핵심
- 서비스명 DNS 사용, 헬스체크 + depends_on(condition: service_healthy)
- RQ 워커는 전용 엔트리포인트에서 `create_app()` 초기화

(예시의 섹션 2 참고)

## 2) 개발 docker-compose.dev.yml 핵심
- 코드 마운트 + 핫 리로드, 디버그 포트, 로컬 Nginx 프록시

(예시의 섹션 3 참고)

## 3) Nginx (운영) 구성 원칙
- Docker DNS `127.0.0.11` + upstream zone/keepalive + API 타임아웃
- backend/front 모두 서비스명 기반으로 동적 재해결

(예시의 석션 4 참고)

## 4) Backend Dockerfile/start.sh 원칙
- 컨테이너는 root로 시작하여 cron/logrotate 실행
- gunicorn은 `appuser`로 권한 다운그레이드
- `/tmp/pdf` 권한 보장, DB init 후 기동

(예시의 섹션 5 참고)

## 5) RQ Worker 엔트리포인트
- `apps/<app>/worker_entrypoint.py`에서 1회 `create_app()` 호출 → 앱 컨텍스트에서 워커 실행
- Task는 Flask 비의존(컨텍스트는 워커가 제공)

(예시의 섹션 6 참고)

## 6) Makefile 운영/개발 공통 진입점
- `ENV=prod|dev`에 따라 compose 명령 전환
- `--wait`는 주요 서비스(backend/frontend/rq-worker/nginx)에만 적용

(예시의 섹션 7 참고)

--------
(예시)

## 섹션 1) 디렉터리 구조(권장)
- 루트
  - `docker-compose.yml` (운영)
  - `docker-compose.dev.yml` (개발 오버레이)
  - `Makefile` (운영/개발 공통 진입점)
  - `nginx/`
    - `conf.d/`
      - `default.conf` (운영)
      - `local.conf` (개발)
    - `Dockerfile`, `Dockerfile.dev`
  - `backend/`
    - `Dockerfile`
    - `start.sh`
    - `app.py` (`create_app()` 팩토리)
    - `apps/…` (도메인/유스케이스/인프라/라우트)
    - `core/…` (공통: 설정/DB/예외/로거)
    - `docs/architecture/…` (설계 문서)
  - `frontend/` (선택)
  - `certbot/` (선택: HTTPS 자동 갱신)

## 섹션 2) docker-compose (운영)
- 목표
  - 서비스명 DNS 사용(고정 IP 의존 제거)
  - `healthcheck + depends_on(condition: service_healthy)`로 초기 502 방지
  - RQ 워커는 전용 엔트리포인트에서 `create_app()` 초기화

```yaml
version: "3.9"
services:
  frontend:
    build: { context: ./frontend, dockerfile: Dockerfile }
    container_name: frontend-container
    ports: ["3000:3000"]
    env_file: [./frontend/.env.production.frontend]
    restart: always
    networks: [app-network]

  backend:
    build: { context: ./backend, dockerfile: Dockerfile }
    container_name: backend-container
    ports: ["5001:5001"]
    volumes:
      - ./backend/logs:/app/logs:rw
      - ./mysql/init:/app/mysql/init:ro
      - ./backend/data:/app/data:ro
      - ./frontend/public/images/main_star:/app/frontend_images:ro
      - pdf_tmp:/tmp/pdf
    env_file: [./backend/.env.production.backend]
    restart: always
    networks: [app-network]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/auth/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    depends_on: [mysql, redis]

  nginx:
    build: { context: ./nginx, dockerfile: Dockerfile }
    container_name: nginx-container
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot
    depends_on:
      frontend: { condition: service_started }
      backend:  { condition: service_healthy }
    networks: [app-network]

  mysql:
    image: mysql:8.0
    container_name: mysql-container
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: appdb
      MYSQL_USER: appuser
      MYSQL_PASSWORD: strongpass
    ports: ["3306:3306"]
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql/init:/docker-entrypoint-initdb.d
      - ./backend/data:/var/lib/mysql-files
    networks: [app-network]
    command: >
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
      --secure-file-priv=/var/lib/mysql-files

  redis:
    image: redis:7-alpine
    container_name: redis
    restart: always
    volumes: [redis_data:/data]
    networks: [app-network]

  rq-worker:
    build: { context: ./backend, dockerfile: Dockerfile, target: production }
    container_name: rq-worker
    user: root
    command: >
      sh -c "su -s /bin/sh -c 'python -m apps.ninestarki.worker_entrypoint' appuser"
    env_file: [./backend/.env.production.backend]
    depends_on: [redis, mysql]
    restart: always
    networks: [app-network]
    volumes: [pdf_tmp:/tmp/pdf]

  certbot:
    image: certbot/certbot
    container_name: certbot-container
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    command: renew --quiet --agree-tos

volumes:
  mysql_data: {}
  redis_data: {}
  pdf_tmp: {}

networks:
  app-network: { driver: bridge }
```

## 섹션 3) docker-compose.dev.yml (개발)
- 코드 마운트, 핫 리로드, 디버그 포트, 로컬 Nginx 프록시

```yaml
services:
  frontend:
    build: { context: ./frontend, dockerfile: Dockerfile, target: development }
    ports: ["3000:3000"]
    volumes: [./frontend:/app, /app/node_modules]
    env_file: [./frontend/.env.development.frontend]
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:3000 || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 40s

  backend:
    build: { context: ./backend, dockerfile: Dockerfile, target: development }
    ports: ["5001:5001", "5678:5678"]
    user: root
    command: >
      sh -c "python /app/wait_for_db.py && python /app/db_manage.py init &&
             chown -R appuser:appgroup /tmp/pdf &&
             exec gunicorn --bind 0.0.0.0:5001 --reload --user appuser --group appgroup 'app:app'"
    volumes: [./backend:/app]
    env_file: [./backend/.env.development.backend]
    depends_on: [mysql, redis]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/auth/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  nginx:
    build: { context: ./nginx, dockerfile: Dockerfile.dev }
    ports: ["80:80"]
    volumes: [./nginx/conf.d/local.conf:/etc/nginx/conf.d/default.conf]
    depends_on:
      frontend: { condition: service_healthy }
      backend:  { condition: service_healthy }

  mysql:
    ports: ["3306:3306"]
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: appdb
      MYSQL_USER: devuser
      MYSQL_PASSWORD: devpass
    volumes: [mysql_data_local:/var/lib/mysql]

  redis:
    ports: ["6379:6379"]

  rq-worker:
    build: { context: ./backend, dockerfile: Dockerfile, target: development }
    env_file: [./backend/.env.development.backend]
    volumes: [./backend:/app]

  backend-test:
    build: { context: ./backend, dockerfile: Dockerfile, target: development }
    volumes: [./backend:/app]
    command: ["tail", "-f", "/dev/null"]

networks:
  app-network: { name: app-network }

volumes:
  mysql_data_local: {}
```

## 섹션 4) Nginx (운영: upstream + 동적 재해결 + keepalive)
- Docker DNS `127.0.0.11` 사용, upstream `zone/keepalive`, API 타임아웃 강화

```nginx
# /etc/nginx/conf.d/default.conf
resolver 127.0.0.11 ipv6=off valid=30s;

upstream fe_upstream {
  zone fe_zone 64k;
  server frontend-container:3000 resolve;
  keepalive 32;
}

upstream be_upstream {
  zone be_zone 64k;
  server backend-container:5001 resolve;
  keepalive 32;
}

server {
  listen 80;
  server_name example.com www.example.com;
  location /.well-known/acme-challenge/ { root /var/www/certbot; }
  location / { return 301 https://$host$request_uri; }
}

server {
  listen 443 ssl;
  server_name example.com www.example.com;
  ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
  include /etc/letsencrypt/options-ssl-nginx.conf;
  ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

  location / {
    proxy_pass http://fe_upstream;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }

  location /api {
    proxy_pass http://be_upstream;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_connect_timeout 10s;
    proxy_read_timeout 60s;
    proxy_send_timeout 60s;
  }
}
```

## 섹션 5) Backend Dockerfile + start.sh (운영)
- 컨테이너는 root로 시작하여 cron/logrotate 등 시스템 작업 수행
- gunicorn은 `appuser`로 권한 다운그레이드 실행

```Dockerfile
FROM python:3.11-slim as base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

FROM base as builder
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libffi-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install gunicorn

FROM base as production
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl logrotate cron default-mysql-client \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-xlib-2.0-0 shared-mime-info fonts-ipafont \
    && rm -rf /var/lib/apt/lists/*
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
RUN pip install -e . && chmod +x /app/start.sh && chmod +x /app/wait_for_db.py && chown -R appuser:appgroup /app
USER root
CMD ["/app/start.sh"]
```

```bash
# start.sh (요약)
set -e
python /app/wait_for_db.py
mkdir -p /app/logs/archive/{access,error,app}; touch /app/logs/{access,error,app}.log
chmod -R 755 /app/logs; chown -R appuser:appgroup /app/logs
python /app/db_manage.py init
service cron start
/usr/sbin/logrotate -f /etc/logrotate.d/gunicorn || true
mkdir -p /tmp/pdf && chown -R appuser:appgroup /tmp/pdf || true
exec su -s /bin/sh -c "gunicorn --bind 0.0.0.0:5001 \
  --log-level debug \
  --access-logfile /app/logs/access.log \
  --error-logfile /app/logs/error.log \
  --capture-output \
  --access-logformat '%(h)s %(l)s %(u)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\" forwarded_for=\"%({X-Forwarded-For}i)s\"' \
  --chdir /app --workers 4 --timeout 90 --worker-class sync --preload 'app:app'" appuser
```

## 섹션 6) RQ Worker (완전 분리 엔트리포인트)
- 전용 엔트리포인트에서 `create_app()` 1회 호출, 앱 컨텍스트 내 Worker 실행
- Task 함수는 Flask 비의존 (컨텍스트는 워커가 제공)

```python
# backend/apps/<app>/worker_entrypoint.py
from redis import Redis
from rq import Worker, Connection
import os, signal

listen = ['pdf_queue']

def main():
    from app import create_app
    app = create_app()
    redis_conn = Redis(host=os.getenv('REDIS_HOST','redis'), port=int(os.getenv('REDIS_PORT',6379)))
    with app.app_context(), Connection(redis_conn):
        worker = Worker(map(str, listen))
        signal.signal(signal.SIGTERM, lambda s,f: (_ for _ in ()).throw(SystemExit(0)))
        worker.work()

if __name__ == '__main__':
    main()
```

```python
# backend/apps/<app>/tasks.py (요약)
from injector import Injector
from core.utils.logger import get_logger
from apps.<app>.use_cases.generate_report_use_case import GenerateReportUseCase

logger = get_logger(__name__)

def generate_pdf_task(report_data: dict, job_id: str):
    logger.info(f"generate_pdf_task | start | job_id={job_id}")
    from apps.<app>.dependency_module import AppModule
    injector = Injector([AppModule()])
    use_case = injector.get(GenerateReportUseCase)
    # ... 최소 입력 재계산 → execute_pdf → /tmp/pdf 저장 ...
```

## 섹션 7) Makefile (운영/개발 공통 진입점)
- `ENV=prod|dev`에 따라 compose 명령 전환
- `--wait`는 주요 서비스만 대상으로 하여 종료형 컨테이너 종료로 인한 실패 방지

```make
ENV ?= prod
ifeq ($(ENV), prod)
  SUDO = sudo
  COMPOSE = $(SUDO) docker compose
else ifeq ($(ENV), dev)
  SUDO =
  COMPOSE = docker compose -f docker-compose.yml -f docker-compose.dev.yml
endif

SERVICES ?= backend frontend rq-worker nginx

up:
	@echo "### [$(ENV)] up --wait $(SERVICES) ###"
	$(COMPOSE) up -d --build --wait $(SERVICES)

rebuild:
	$(COMPOSE) build --no-cache
	$(COMPOSE) up -d --wait $(SERVICES)

restart-be:
	$(COMPOSE) restart backend
```

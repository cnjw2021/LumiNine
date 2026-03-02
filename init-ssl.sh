#!/bin/bash

# ==============================================================================
# SSL 인증서 초기 발급 스크립트 (최초 1회만 실행)
# ==============================================================================
# Let's Encrypt SSL 인증서를 발급합니다.
# 이미 인증서가 존재하는 경우 이 스크립트를 실행할 필요가 없습니다.
#
# 사전 요구사항:
#   - 도메인의 DNS A 레코드가 이 서버 IP를 가리키고 있어야 합니다
#   - 80 포트가 열려 있어야 합니다
# ==============================================================================

# --- 설정값 (환경에 맞게 수정) ---
domains=(831shop.site www.831shop.site)
email="hopstepjump1015@gmail.com"   # Let's Encrypt 알림 수신 이메일
COMPOSE_FILE="docker-compose.prod.yml"
# --- 설정값 끝 ---

set -e

echo "### 필요한 디렉토리를 생성합니다... ###"
mkdir -p ./certbot/conf ./certbot/www

echo "### 임시 Nginx 설정 파일을 생성합니다... ###"
# SSL 설정 없이 80 포트만 열어 certbot 인증에 사용
cat > ./certbot/conf/default.conf <<EOF
events {
    worker_connections 1024;
}
http {
    server {
        listen 80;
        server_name ${domains[0]} ${domains[1]};

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 200 'SSL 인증서 발급 대기 중...';
        }
    }
}
EOF

echo "### 임시 Nginx 컨테이너를 백그라운드로 실행합니다... ###"
docker compose -f ${COMPOSE_FILE} run --rm -d --name nginx-temp --service-ports \
  -v "$(pwd)/certbot/conf:/etc/nginx/conf.d" \
  -v "$(pwd)/certbot/www:/var/www/certbot" \
  --entrypoint "\
  nginx -g 'daemon off;' -c /etc/nginx/conf.d/default.conf" nginx

echo "### SSL 인증서 발급을 요청합니다... ###"
docker compose -f ${COMPOSE_FILE} run --rm certbot certonly --webroot --webroot-path=/var/www/certbot \
    --email $email \
    --agree-tos \
    --no-eff-email \
    -d ${domains[0]} -d ${domains[1]}

echo "### 임시 Nginx 컨테이너를 중지합니다... ###"
docker stop nginx-temp

echo "### 임시 Nginx 설정 파일을 삭제합니다... ###"
rm ./certbot/conf/default.conf

echo "### SSL 보안 옵션 파일을 생성합니다... ###"
mkdir -p ./certbot/conf
cat > ./certbot/conf/options-ssl-nginx.conf <<EOF
ssl_session_cache shared:le_nginx_SSL:10m;
ssl_session_timeout 1440m;
ssl_session_tickets off;

ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;

ssl_ciphers "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384";
EOF

echo "### Diffie-Hellman 파라미터 파일을 생성합니다... ###"
if [ ! -f "./certbot/conf/ssl-dhparams.pem" ]; then
  openssl dhparam -out ./certbot/conf/ssl-dhparams.pem 2048
fi

# Crontab에 인증서 자동 갱신 등록 (매일 02:30)
echo "### Crontab에 자동 갱신 작업을 등록합니다... ###"
PROJECT_PATH=$(pwd)
CRON_COMMAND="/usr/bin/docker compose -f $PROJECT_PATH/${COMPOSE_FILE} run --rm certbot renew && /usr/bin/docker compose -f $PROJECT_PATH/${COMPOSE_FILE} exec nginx nginx -s reload"
CRON_JOB="30 2 * * * $CRON_COMMAND"

(crontab -l 2>/dev/null | grep -Fq "$CRON_COMMAND") || \
( (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab - && \
echo "성공: Crontab에 자동 갱신 작업이 추가되었습니다." )

echo "### SSL 초기 설정이 완료되었습니다! ###"
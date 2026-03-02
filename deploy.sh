#!/bin/bash
set -e

# ==============================================================================
# 수동 배포 스크립트 (ConoHa 서버용)
# ==============================================================================
# GitHub Actions CI가 빌드한 GHCR 이미지를 Pull하여 배포합니다.
#
# 사전 요구사항:
#   1. GHCR 로그인: docker login ghcr.io -u <GITHUB_USER> -p <GITHUB_TOKEN>
#   2. 서버에 아래 파일들이 존재해야 합니다:
#      - docker-compose.prod.yml
#      - .env.production.backend
#      - .env.production.frontend
#      - nginx/conf.d/  (nginx 설정)
#      - certbot/       (SSL 인증서)
#      - mysql/init/    (DB 초기화 스크립트, 최초 배포 시)
# ==============================================================================

COMPOSE_FILE="docker-compose.prod.yml"
REGISTRY="ghcr.io/cnjw2021/ninestar-compact"

# --------------------------------------------------
# 환경변수 로드 (docker-compose 파일의 ${...} 치환을 위함)
# --------------------------------------------------
if [ -f ".env.production.backend" ]; then
    set -a
    source .env.production.backend
    set +a
else
    echo -e "\033[0;31m❌ .env.production.backend 파일을 찾을 수 없습니다.\033[0m"
    exit 1
fi

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}===== 배포 시작 =====${NC}"
echo ""

# --------------------------------------------------
# 0. 기존 컨테이너 중지 (포트 충돌 방지)
# --------------------------------------------------
echo -e "${YELLOW}0. 기존 컨테이너 중지 중...${NC}"
docker compose -f ${COMPOSE_FILE} down
# 이전의 init-ssl.sh 실행 중 중단으로 인해 남아있는 임시 Nginx 컨테이너도 강제 종료 처리
docker rm -f nginx-temp >/dev/null 2>&1 || true
echo ""

# --------------------------------------------------
# SSL 인증서 및 보안 파일 확인/복구
# --------------------------------------------------
DOMAIN="831shop.site"

# 1. Nginx 기본 보안 파일 복구 (init-ssl.sh가 중간에 끊겼을 때 대비)
if [ ! -f "certbot/conf/options-ssl-nginx.conf" ]; then
    echo -e "${YELLOW}👉 SSL 보안 옵션 파일이 없습니다. 자동으로 생성합니다...${NC}"
    mkdir -p ./certbot/conf
    cat > ./certbot/conf/options-ssl-nginx.conf <<EOF
ssl_session_cache shared:le_nginx_SSL:10m;
ssl_session_timeout 1440m;
ssl_session_tickets off;

ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;

ssl_ciphers "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384";
EOF
fi

if [ ! -f "certbot/conf/ssl-dhparams.pem" ]; then
    echo -e "${YELLOW}👉 SSL DH 파라미터가 없습니다. 자동으로 생성합니다 (수 분 소요될 수 있음)...${NC}"
    openssl dhparam -out ./certbot/conf/ssl-dhparams.pem 2048
fi

# 2. 인증서 실존 여부를 Docker 권한으로 체크 (certbot 폴더가 root 소유라 일반 권한으로 안 보일 수 있음)
docker pull ${REGISTRY}-nginx:latest >/dev/null 2>&1 || true
HAS_CERT=$(docker run --rm -v "$(pwd)/certbot/conf:/etc/letsencrypt" ${REGISTRY}-nginx:latest sh -c "test -f /etc/letsencrypt/live/${DOMAIN}/fullchain.pem && echo 'yes' || echo 'no'")

if [ "$HAS_CERT" = "no" ]; then
    echo -e "${YELLOW}👉 SSL 인증서가 없습니다. 최초 발급 스크립트(init-ssl.sh)를 자동으로 실행합니다...${NC}"
    if [ ! -x "init-ssl.sh" ]; then
        chmod +x init-ssl.sh
    fi
    ./init-ssl.sh
    echo -e "${GREEN}✅ SSL 인증서 발급 완료. 배포를 계속합니다...${NC}"
    echo ""
else
    echo -e "${GREEN}✅ 기존 SSL 인증서(${DOMAIN})가 확인되었습니다. 발급을 건너뜁니다.${NC}"
    echo ""
fi

# --------------------------------------------------
# 1. 최신 이미지 가져오기
# --------------------------------------------------
echo -e "${YELLOW}1. 최신 이미지 가져오기${NC}"
docker pull ${REGISTRY}-frontend:latest
docker pull ${REGISTRY}-backend:latest
docker pull ${REGISTRY}-nginx:latest
echo ""

# --------------------------------------------------
# 1.5. 이미지에서 CSV 데이터 추출 (MySQL LOAD DATA 용)
# --------------------------------------------------
echo -e "${YELLOW}1.5. 백엔드 이미지에서 CSV 데이터를 추출하여 호스트에 복사합니다...${NC}"
mkdir -p ./backend/data/csv
# 기존 권한(mysql이 소유) 문제 방지를 위해 컨테이너를 root로 실행하여 덮어쓰기
docker run --rm --user root -v "$(pwd)/backend/data/csv:/host_csv" ${REGISTRY}-backend:latest sh -c "rm -rf /host_csv/* && cp -a /app/data/csv/. /host_csv/ && chown -R 999:999 /host_csv && chmod -R 755 /host_csv"
echo -e "${GREEN}   ✅ CSV 데이터 복사 완료${NC}"
echo ""


# --------------------------------------------------
# 2. 새 컨테이너 실행
# --------------------------------------------------
echo -e "${YELLOW}2. 새 컨테이너 실행${NC}"
docker compose -f ${COMPOSE_FILE} up -d
echo ""

# --------------------------------------------------
# 3. 헬스체크 대기
# --------------------------------------------------
echo -e "${YELLOW}3. 백엔드 헬스체크 대기 (최대 60초)${NC}"
RETRY=0
MAX_RETRY=12
until docker exec backend-container curl -sf http://localhost:5001/auth/health > /dev/null 2>&1; do
    RETRY=$((RETRY + 1))
    if [ $RETRY -ge $MAX_RETRY ]; then
        echo -e "${RED}❌ 백엔드 헬스체크 실패! 로그를 확인하세요:${NC}"
        echo "   docker compose -f ${COMPOSE_FILE} logs backend"
        exit 1
    fi
    echo "   대기 중... (${RETRY}/${MAX_RETRY})"
    sleep 5
done
echo -e "${GREEN}   ✅ 백엔드 정상 기동 확인${NC}"
echo ""

# --------------------------------------------------
# 4. 데이터베이스 초기화 (안전한 init)
# --------------------------------------------------
# 테이블이 없으면 생성하고, 슈퍼유저가 없으면 생성합니다 (기존 데이터 유지)
echo -e "${YELLOW}4. 데이터베이스 안전 초기화 (슈퍼유저 확인 등)${NC}"
docker exec backend-container python db_manage.py init
echo -e "${GREEN}   ✅ 데이터베이스 초기화 완료${NC}"
echo ""

# --------------------------------------------------
# 5. 사용하지 않는 구버전 이미지 정리
# --------------------------------------------------
echo -e "${YELLOW}5. 구버전 이미지 정리${NC}"
docker image prune -f
echo ""

# --------------------------------------------------
# 완료
# --------------------------------------------------
echo -e "${GREEN}===== 배포 완료! =====${NC}"
echo ""
docker compose -f ${COMPOSE_FILE} ps

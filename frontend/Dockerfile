# ===================================================================
#  1. base - 모든 환경의 기반이 되는 최소 스테이지
# ===================================================================
FROM node:20-alpine as base
WORKDIR /app

# ===================================================================
#  2. deps - 의존성 설치 전용 스테이지
# ===================================================================
FROM base as deps
COPY package.json package-lock.json* ./
# 운영 환경에 필요한 의존성만 설치 (npm ci는 package-lock.json을 사용)
RUN npm install --legacy-peer-deps

# ===================================================================
#  3. development - 개발 환경 스테이지
# ===================================================================
FROM base as development
# 개발에 필요한 도구 설치 (필요 시)
RUN apk add --no-cache curl

# deps 스테이지에서 설치한 node_modules를 복사
COPY --from=deps /app/node_modules /app/node_modules
COPY package.json package-lock.json* ./

# 개발 서버 실행 (docker-compose.dev.yml에서 코드는 볼륨 마운트)
CMD ["npm", "run", "dev"]

# ===================================================================
#  4. builder - 운영 환경 빌드 전용 스테이지
# ===================================================================
FROM deps as builder
# 애플리케이션 전체 소스 코드 복사
COPY . .
# 운영 환경용 .env 파일 복사
COPY .env.production.frontend .env.local
# Next.js 애플리케이션 빌드
RUN npm run build

# ===================================================================
#  5. production - 최종 운영 환경 스테이지 (기본값)
# ===================================================================
FROM base as production
ENV NODE_ENV=production

# 보안을 위한 non-root 사용자 생성
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# builder 스테이지에서 빌드된 결과물만 복사
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# non-root 사용자로 전환
USER nextjs

EXPOSE 3000
CMD ["npm", "run", "start"]

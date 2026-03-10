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
#  3. development - 開発環境ステージ (docker-compose で使用)
#  ※ 本番環境は Cloudflare Pages でビルド・デプロイするため
#    Docker の production ステージは不要
# ===================================================================
FROM base as development
# 開発に必要なツール設置 (必要時)
RUN apk add --no-cache curl

# deps ステージで設置した node_modules を復元
COPY --from=deps /app/node_modules /app/node_modules
COPY package.json package-lock.json* ./

# 開発サーバー実行 (docker-compose でコードはボリュームマウント)
CMD ["npm", "run", "dev"]

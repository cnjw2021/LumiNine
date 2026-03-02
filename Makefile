# Makefile

# 基本環境を 'prod' (運用) に設定します。
ENV ?= prod

# ENV 値に応じて sudo と docker compose コマンドを動的に設定します。
ifeq ($(ENV), prod)
	SUDO = sudo
	COMPOSE = $(SUDO) docker compose
else ifeq ($(ENV), dev)
	SUDO =
	COMPOSE = docker compose -f docker-compose.yml -f docker-compose.dev.yml
endif

.PHONY: bootstrap setup up down stop restart logs renew help db-reset prune build-be rebuild-be restart-be restart-worker logs-be build-fe rebuild-fe restart-fe logs-fe gen-pngs
.DEFAULT_GOAL := help

# 待機対象とする主要サービス（certbot は除外してエラーを回避）
SERVICES ?= backend frontend rq-worker nginx


# ==============================================================================
# 🚀 サーバーとプロジェクトの設定
# ==============================================================================
bootstrap: ## ✨ [運用] 新しいサーバーに Docker などの必須ツールをインストールします。
	@chmod +x ./bootstrap.sh
	sudo ./bootstrap.sh

setup: ## 🚀 [運用] SSL 証明書を含むプロジェクトをデプロイします。
	@echo "### [1/5] ゴースト コンテナを強制的にクリーンアップします... ###"
	$(SUDO) docker stop nginx-temp || true
	$(SUDO) docker rm nginx-temp || true
	@echo "### [2/5] 既存のコンテナをすべて停止して削除します... ###"
	$(COMPOSE) down
	@echo "### [3/5] プロジェクトの初期設定を開始します... ###"
	@chmod +x ./init-ssl.sh
	sudo ./init-ssl.sh
	@echo "### リソースの解放を待機しています... (10秒) ###"
	sleep 10
	@echo "### [4/5] SSL 設定完了。最終アプリケーションを開始します... ###"
	$(COMPOSE) up -d --build --wait $(SERVICES)
	@echo "### [5/5] デプロイが完了しました! ###"

# ==============================================================================
# 🐳 アプリケーション管理
# ==============================================================================
up: ## 🐳 アプリケーションを開始/更新します。(例: make up ENV=dev)
	@echo "### [$(ENV)] 環境のアプリケーションを開始/更新します... ###"
	$(COMPOSE) up -d --build --wait $(SERVICES)

rebuild: ## 🔄 [注意] キャッシュを無視して、アプリケーションを完全に再構築します。
	@echo "### [$(ENV)] 環境のアプリケーションをキャッシュなしで再構築します... ###"
	# キャッシュを無視して、アプリケーションを再構築します。
	$(COMPOSE) build --no-cache
# 新しいイメージでアプリケーションを開始します。
	$(COMPOSE) up -d --wait $(SERVICES)

down: ## ⛔️ アプリケーションコンテナを停止/削除します。(例: make down ENV=dev)
	@echo "### [$(ENV)] 環境のアプリケーションを停止します... ###"
	$(SUDO) docker stop nginx-temp || true
	$(SUDO) docker rm nginx-temp || true
	$(COMPOSE) down

down-v: ## 💥 [注意] コンテナとデータボリュームをすべて削除します。
	@echo "### [$(ENV)] 環境のアプリケーションを停止し、ボリュームを削除します... ###"
	$(COMPOSE) down -v

stop: ## ⛔️ 実行中のすべてのコンテナを停止します。(注意)
	@echo "### [$(ENV)] 環境のすべてのコンテナを停止します... ###"
	@if [ -n "$$(docker ps -q)" ]; then \
		docker stop $$(docker ps -q); \
	else \
		echo "実行中のコンテナはありません。"; \
	fi

restart: ## 🔄 サービスを再起動します。(例: make restart ENV=dev)
	@echo "### [$(ENV)] 環境のアプリケーションを再起動します... ###"
	$(COMPOSE) restart

# ==============================================================================
# 🔧 バックエンド専用管理
# ==============================================================================
build-be: ## 🔧 バックエンドのみをビルドします。(例: make build-be ENV=dev)
	@echo "### [$(ENV)] 環境のバックエンドのみをビルドします... ###"
	$(COMPOSE) build backend

rebuild-be: ## 🔄 バックエンドのみをキャッシュなしで再構築します。(例: make rebuild-be ENV=dev)
	@echo "### [$(ENV)] 環境のバックエンドのみをキャッシュなしで再構築します... ###"
	$(COMPOSE) build --no-cache backend
	$(COMPOSE) up -d backend

restart-be: ## 🔄 バックエンド+ワーカーを再起動します。(例: make restart-be ENV=dev)
	@echo "### [$(ENV)] 環境のバックエンド+ワーカーを再起動します... ###"
	$(COMPOSE) restart backend rq-worker

restart-worker: ## 🔄 ワーカーのみを再起動します。(例: make restart-worker ENV=dev)
	@echo "### [$(ENV)] 環境のワーカーのみを再起動します... ###"
	$(COMPOSE) restart rq-worker

gen-pngs: ## 🖼️ PDF用の九星盤PNGを事前生成します。(例: make gen-pngs ENV=dev)
	@echo "### [$(ENV)] 環境で九星盤PNGを事前生成します... ###"
	$(COMPOSE) run --rm backend python scripts/generate_main_star_pngs.py --size 900

logs-be: ## 📜 バックエンドの実時間ログを確認します。(例: make logs-be ENV=dev)
	@echo "### [$(ENV)] 環境のバックエンド実時間ログを出力します... ###"
	$(COMPOSE) logs -f backend

# ==============================================================================
# 🎨 フロントエンド専用管理
# ==============================================================================
build-fe: ## 🎨 フロントエンドのみをビルドします。(例: make build-fe ENV=dev)
	@echo "### [$(ENV)] 環境のフロントエンドのみをビルドします... ###"
	$(COMPOSE) build frontend

rebuild-fe: ## 🔄 フロントエンドのみをキャッシュなしで再構築します。(文言修正などの反映)
	@echo "### [$(ENV)] 環境のフロントエンドのみをキャッシュなしで再構築します... ###"
	$(COMPOSE) build --no-cache frontend
	$(COMPOSE) up -d frontend

restart-fe: ## 🔄 フロントエンドのみを再起動します。(例: make restart-fe ENV=dev)
	@echo "### [$(ENV)] 環境のフロントエンドのみを再起動します... ###"
	$(COMPOSE) restart frontend

logs-fe: ## 📜 フロントエンドの実時間ログを確認します。(例: make logs-fe ENV=dev)
	@echo "### [$(ENV)] 環境のフロントエンド実時間ログを出力します... ###"
	$(COMPOSE) logs -f frontend

logs: ## 📜 実時間ログを確認します。(例: make logs ENV=dev)
	@echo "### [$(ENV)] 環境の実時間ログを出力します... ###"
	$(COMPOSE) logs -f

test: ## 🧪 Dockerコンテナ内でテストを実行します。
	@echo "### [dev] Dockerコンテナ内でテストを実行します... ###"
	@echo "テストが終了すると、テスト専用コンテナは自動的に停止され、削除されます。(--rm)"
	# 新しいbackend-testサービスを使用してpytestを実行
	docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm backend-test pytest

test-unit: ## 🧪 単体テストのみ実行します。(CI用: DB不要)
	@echo "### [dev] 単体テストのみ実行します... ###"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm backend-test pytest --ignore=tests/golden_master --ignore=tests/test_direction_fortune_birthdate_2026.py -v

test-integration: ## 🧪 統合テストのみ実行します。(DB + バックエンドAPI必須)
	@echo "### [dev] 統合テストのみ実行します... ###"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm backend-test pytest tests/golden_master tests/test_direction_fortune_birthdate_2026.py -v


# ==============================================================================
# 🔐 データベースとシステムの管理
# ==============================================================================
db-seed: ## 🌱 データベースを完全にリセットし、全データ（SQL + CSV）を再投入します。
	@echo "### データベースを完全にシード（SQL + CSV）します... ###"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm backend-test python db_manage.py reset

db-init: ## ✅ [安全] DBが空の場合にのみテーブル作成と初期データ挿入
	@echo "### データベースを安全に初期化します... ###"
	$(COMPOSE) run --rm backend python db_manage.py init

db-reset: ## 💥 [注意] DBを完全に初期化します。すべてのデータが削除されます。
	@echo "### データベースをリセットします! すべてのデータが削除されます... ###"
	$(COMPOSE) run --rm backend python db_manage.py reset

# --- 🚀 プロダクション(本番)環境専用コマンド ---
prod-mysql-restart: ## 🔄 [運用] 本番環境のMySQLコンテナを再起動します。
	@echo "### 本番環境のMySQLを再起動します... ###"
	docker compose --env-file .env.production.backend -f docker-compose.prod.yml down mysql
	docker compose --env-file .env.production.backend -f docker-compose.prod.yml up -d mysql

prod-db-reset: ## 💥 [注意/運用] 本番環境の稼働中コンテナでDBをリセットします。
	@echo "### 本番環境のデータベースをリセットし、初期データをシードします... ###"
	docker exec backend-container python db_manage.py reset
# ---------------------------------------------

renew: ## 🔐 [運用] SSL 証明書を手動で更新します。
	@echo "### SSL 証明書を更新します... ###"
	$(COMPOSE) run --rm certbot renew

prune: ## 🧹 [注意] 停止したすべてのコンテナ、使用されないリソースを削除します。
	@echo "### Docker システムを整理します... ###"
	$(SUDO) docker system prune -af

help: ## ℹ️ 使用可能なすべてのコマンドを表示します。
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
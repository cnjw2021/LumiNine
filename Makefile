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

# PR 리뷰 자동화 설정
PR_REVIEW_DIR ?= .pr-review
PR_BATCH_LIMIT ?= 5



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

debug-directions: ## 🔍 方位吉凶デバッグ (例: make debug-directions MAIN_STAR=5 MONTH_STAR=3)
	@echo "### 方位吉凶デバッグスクリプトを実行します... ###"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm \
	  -e MAIN_STAR="$(or $(MAIN_STAR),5)" \
	  -e MONTH_STAR="$(or $(MONTH_STAR),3)" \
	  -e TARGET_YEAR="$(or $(TARGET_YEAR),2026)" \
	  -e SETSU_MONTH="$(or $(SETSU_MONTH),2)" \
	  backend-test python scripts/debug_directions.py


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


# ── PR 리뷰 코멘트 triage 자동화 ──

pr-flow: pr-triage
	@if [ -z "$(PR)" ]; then echo "사용법: make pr-flow PR=<번호> [BATCH=$(PR_BATCH_LIMIT)]"; exit 1; fi
	@echo ""
	@echo "=== PR 리뷰 자동화 다음 단계 ==="
	@echo "생성 파일:"
	@echo "  - $(PR_REVIEW_DIR)/pr-$(PR)-triage.md"
	@echo "  - $(PR_REVIEW_DIR)/pr-$(PR)-autofix-checklist.md"
	@echo "  - $(PR_REVIEW_DIR)/pr-$(PR)-reply-batch.json"
	@echo ""
	@AUTO_FIXABLE=$$(awk '/^- Auto-fixable:/ {print $$3; exit}' $(PR_REVIEW_DIR)/pr-$(PR)-triage.md 2>/dev/null || echo 0); \
	MANUAL=$$(awk '/^- Needs [Mm]anual [Vv]erification/ {print $$NF; exit}' $(PR_REVIEW_DIR)/pr-$(PR)-triage.md 2>/dev/null || echo 0); \
	DESIGN=$$(awk '/^- Needs design review:/ {print $$5; exit}' $(PR_REVIEW_DIR)/pr-$(PR)-triage.md 2>/dev/null || echo 0); \
	echo "권장 순서:"; \
	echo "  1) triage 결과 기준으로 수정/테스트/커밋/푸시"; \
	if [ "$$AUTO_FIXABLE" -gt 0 ]; then \
		echo "  2) make pr-reply-batch PR=$(PR)   # auto-fixable=$$AUTO_FIXABLE"; \
	fi; \
	if [ "$$MANUAL" -gt 0 ] || [ "$$DESIGN" -gt 0 ]; then \
		echo "  3) make pr-manual-flow PR=$(PR)   # manual+design=$$(($$MANUAL + $$DESIGN))"; \
	fi; \
	if [ "$$AUTO_FIXABLE" -eq 0 ] && [ "$$MANUAL" -eq 0 ] && [ "$$DESIGN" -eq 0 ]; then \
		echo "  2) reply/resolve 대상 코멘트가 없습니다 (0/0 예상)"; \
	fi; \
	echo "     (이미 handled된 코멘트에 정정 reply가 필요하면: make pr-manual-fix-flow PR=$(PR))"

pr-flow-next: pr-triage-next
	@if [ -z "$(PR)" ]; then echo "사용법: make pr-flow-next PR=<번호> OFFSET=<숫자> [BATCH=$(PR_BATCH_LIMIT)]"; exit 1; fi
	@if [ -z "$(OFFSET)" ]; then echo "사용법: make pr-flow-next PR=<번호> OFFSET=<숫자> [BATCH=$(PR_BATCH_LIMIT)]"; exit 1; fi
	@echo ""
	@echo "=== PR 리뷰 자동화 다음 배치 안내 ==="
	@echo "배치 파라미터:"
	@echo "  - OFFSET=$(OFFSET)"
	@echo "  - BATCH=$(or $(BATCH),$(PR_BATCH_LIMIT))"
	@echo "생성 파일(동일 경로에 최신 배치 기준으로 갱신됨):"
	@echo "  - $(PR_REVIEW_DIR)/pr-$(PR)-triage.md"
	@echo "  - $(PR_REVIEW_DIR)/pr-$(PR)-autofix-checklist.md"
	@echo "  - $(PR_REVIEW_DIR)/pr-$(PR)-reply-batch.json"
	@echo ""
	@AUTO_FIXABLE=$$(awk '/^- Auto-fixable included in this batch:/ {print $$7; exit}' $(PR_REVIEW_DIR)/pr-$(PR)-triage.md 2>/dev/null | cut -d'/' -f1); \
	AUTO_FIXABLE=$${AUTO_FIXABLE:-0}; \
	echo "권장 순서:"; \
	echo "  1) 이번 배치(offset=$(OFFSET)) 항목 수정/테스트/커밋/푸시"; \
	if [ "$$AUTO_FIXABLE" -gt 0 ]; then \
		echo "  2) make pr-reply-batch PR=$(PR)   # auto-fixable batch=$$AUTO_FIXABLE"; \
	else \
		echo "  2) auto-fixable 배치가 비어 있습니다. manual/design 코멘트면 make pr-manual-flow PR=$(PR) 사용"; \
	fi

pr-triage:
	@if [ -z "$(PR)" ]; then echo "사용법: make pr-triage PR=<번호> [BATCH=$(PR_BATCH_LIMIT)]"; exit 1; fi
	npm run pr:triage -- $(PR) \
	  --limit-auto-fix $(or $(BATCH),$(PR_BATCH_LIMIT)) \
	  --emit-reply-batch \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-triage-next:
	@if [ -z "$(PR)" ]; then echo "사용법: make pr-triage-next PR=<번호> OFFSET=<숫자> [BATCH=$(PR_BATCH_LIMIT)]"; exit 1; fi
	@if [ -z "$(OFFSET)" ]; then echo "사용법: make pr-triage-next PR=<번호> OFFSET=<숫자> [BATCH=$(PR_BATCH_LIMIT)]"; exit 1; fi
	npm run pr:triage -- $(PR) \
	  --offset-auto-fix $(OFFSET) \
	  --limit-auto-fix $(or $(BATCH),$(PR_BATCH_LIMIT)) \
	  --emit-reply-batch \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-triage-manual:
	@if [ -z "$(PR)" ]; then echo "사용법: make pr-triage-manual PR=<번호> [BATCH=$(PR_BATCH_LIMIT)] [OFFSET=<숫자>]"; exit 1; fi
	npm run pr:triage -- $(PR) \
	  $(if $(OFFSET),--offset-auto-fix $(OFFSET),) \
	  --limit-auto-fix $(or $(BATCH),$(PR_BATCH_LIMIT)) \
	  --emit-manual-reply-batch \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-triage-manual-fix:
	@if [ -z "$(PR)" ]; then echo "사용법: make pr-triage-manual-fix PR=<번호> [BATCH=$(PR_BATCH_LIMIT)] [OFFSET=<숫자>]"; exit 1; fi
	npm run pr:triage -- $(PR) \
	  $(if $(OFFSET),--offset-auto-fix $(OFFSET),) \
	  --limit-auto-fix $(or $(BATCH),$(PR_BATCH_LIMIT)) \
	  --emit-manual-reply-batch \
	  --include-resolved \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-reply-batch:
	@if [ -z "$(PR)" ]; then echo "사용법: make pr-reply-batch PR=<번호>"; exit 1; fi
	npm run pr:review-reply -- \
	  --batch-file $(PR_REVIEW_DIR)/pr-$(PR)-reply-batch.json \
	  --continue-on-error \
	  --failed-batch-out $(PR_REVIEW_DIR)/pr-$(PR)-reply-batch.failed.json \
	  --log-file $(PR_REVIEW_DIR)/reply-actions.ndjson \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-reply-batch-retry:
	@if [ -z "$(PR)" ]; then echo "사용법: make pr-reply-batch-retry PR=<번호>"; exit 1; fi
	npm run pr:review-reply -- \
	  --batch-file $(PR_REVIEW_DIR)/pr-$(PR)-reply-batch.failed.json \
	  --continue-on-error \
	  --failed-batch-out $(PR_REVIEW_DIR)/pr-$(PR)-reply-batch.failed.next.json \
	  --log-file $(PR_REVIEW_DIR)/reply-actions.ndjson \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-reply-batch-manual:
	@if [ -z "$(PR)" ]; then echo "사용법: make pr-reply-batch-manual PR=<번호>"; exit 1; fi
	@if [ ! -f "$(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.json" ]; then \
		echo "manual reply batch 파일이 없습니다: $(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.json"; \
		echo "먼저 실행: make pr-triage-manual PR=$(PR)"; \
		echo "이미 handled된 코멘트 정정 reply가 목적이면: make pr-triage-manual-fix PR=$(PR)"; \
		exit 1; \
	fi
	npm run pr:review-reply -- \
	  --batch-file $(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.json \
	  --continue-on-error \
	  --failed-batch-out $(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.failed.json \
	  --log-file $(PR_REVIEW_DIR)/reply-actions.ndjson \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-reply-batch-manual-force:
	@if [ -z "$(PR)" ]; then echo "사용법: make pr-reply-batch-manual-force PR=<번호>"; exit 1; fi
	@if [ ! -f "$(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.json" ]; then \
		echo "manual reply batch 파일이 없습니다: $(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.json"; \
		echo "먼저 실행: make pr-triage-manual-fix PR=$(PR)"; \
		exit 1; \
	fi
	npm run pr:review-reply -- \
	  --batch-file $(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.json \
	  --continue-on-error \
	  --failed-batch-out $(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.failed.json \
	  --log-file $(PR_REVIEW_DIR)/reply-actions.ndjson \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-manual-flow: pr-triage-manual pr-reply-batch-manual
	@if [ -z "$(PR)" ]; then echo "사용법: make pr-manual-flow PR=<번호> [BATCH=$(PR_BATCH_LIMIT)] [OFFSET=<숫자>]"; exit 1; fi
	@echo ""
	@echo "=== Manual(review + design-review) reply 처리 완료 ==="
	@echo "실행 항목:"
	@echo "  1) make pr-triage-manual PR=$(PR) $(if $(OFFSET),OFFSET=$(OFFSET),) $(if $(BATCH),BATCH=$(BATCH),)"
	@echo "  2) make pr-reply-batch-manual PR=$(PR)"

pr-manual-fix-flow: pr-triage-manual-fix pr-reply-batch-manual-force
	@if [ -z "$(PR)" ]; then echo "사용법: make pr-manual-fix-flow PR=<번호> [BATCH=$(PR_BATCH_LIMIT)] [OFFSET=<숫자>]"; exit 1; fi
	@echo ""
	@echo "=== Manual 정정 reply 처리 완료 ==="
	@echo "실행 항목:"
	@echo "  1) make pr-triage-manual-fix PR=$(PR) $(if $(OFFSET),OFFSET=$(OFFSET),) $(if $(BATCH),BATCH=$(BATCH),)"
	@echo "  2) make pr-reply-batch-manual-force PR=$(PR)"

pr-followup: pr-triage
	@if [ -z "$(PR)" ]; then echo "사용법: make pr-followup PR=<번호> [BATCH=$(PR_BATCH_LIMIT)] [OFFSET=<숫자>]"; exit 1; fi
	@AUTO_FIXABLE=$$(awk '/^- Auto-fixable:/ {print $$3; exit}' $(PR_REVIEW_DIR)/pr-$(PR)-triage.md 2>/dev/null || echo 0); \
	MANUAL=$$(awk '/^- Needs [Mm]anual [Vv]erification/ {print $$NF; exit}' $(PR_REVIEW_DIR)/pr-$(PR)-triage.md 2>/dev/null || echo 0); \
	DESIGN=$$(awk '/^- Needs design review:/ {print $$5; exit}' $(PR_REVIEW_DIR)/pr-$(PR)-triage.md 2>/dev/null || echo 0); \
	if [ "$$AUTO_FIXABLE" -gt 0 ]; then \
		echo "=== Auto-fixable reply/resolve 배치 실행 ==="; \
		$(MAKE) pr-reply-batch PR=$(PR); \
	else \
		echo "=== Auto-fixable reply/resolve 대상 없음 ==="; \
	fi; \
	if [ "$$MANUAL" -gt 0 ] || [ "$$DESIGN" -gt 0 ]; then \
		echo "=== Manual/Design-review reply/resolve 배치 실행 ==="; \
		$(MAKE) pr-manual-flow PR=$(PR) $(if $(OFFSET),OFFSET=$(OFFSET),) $(if $(BATCH),BATCH=$(BATCH),); \
	else \
		echo "=== Manual/Design-review reply/resolve 대상 없음 ==="; \
	fi
	@echo ""
	@echo "=== PR 후속 처리 안내 (반복 작업 완료) ==="
	@echo "완료:"
	@echo "  - triage 실행"
	@echo "  - auto-fixable reply/resolve 배치 실행 (있을 때)"
	@echo "  - manual/design reply/resolve 배치 실행 (있을 때)"
	@echo ""
	@echo "다음 단계(순서 중요):"
	@echo "  1) 수정/테스트/커밋/푸시가 추가로 있었다면 PR 제목/본문 업데이트"
	@echo "  2) (auto/manual 혼합 포함) 모든 reply/resolve 반영 후 Copilot 리뷰 재요청"
	@echo "     - 현재 PR에서 Copilot 리뷰가 이미 완료된 경우 skip"

pr-edit-meta:
	@if [ -z "$(PR)" ]; then echo "사용법: make pr-edit-meta PR=<번호> [TITLE=\"제목\"] [BODY_FILE=/tmp/pr<번호>_body.md] [TITLE_FILE=/tmp/pr<번호>_title.txt]"; exit 1; fi
	@BODY_FILE_PATH="$(if $(BODY_FILE),$(BODY_FILE),/tmp/pr$(PR)_body.md)"; \
	TITLE_FILE_PATH="$(if $(TITLE_FILE),$(TITLE_FILE),/tmp/pr$(PR)_title.txt)"; \
	TITLE_VALUE="$(TITLE)"; \
	if [ -z "$$TITLE_VALUE" ]; then \
		if [ ! -f "$$TITLE_FILE_PATH" ]; then \
			echo "TITLE 미지정이고 제목 파일도 없습니다: $$TITLE_FILE_PATH"; \
			echo "사용법: make pr-edit-meta PR=$(PR) TITLE=\"제목\""; \
			exit 1; \
		fi; \
		TITLE_VALUE="$$(cat "$$TITLE_FILE_PATH")"; \
	fi; \
	if [ ! -f "$$BODY_FILE_PATH" ]; then \
		echo "본문 파일이 없습니다: $$BODY_FILE_PATH"; \
		echo "예시: /tmp/pr$(PR)_body.md"; \
		exit 1; \
	fi; \
	echo "=== GH 인증 상태 확인 ==="; \
	gh auth status || true; \
	echo ""; \
	echo "=== PR #$(PR) 제목/본문 업데이트 ==="; \
	echo "Title: $$TITLE_VALUE"; \
	echo "Body : $$BODY_FILE_PATH"; \
	gh pr edit $(PR) --title "$$TITLE_VALUE" --body-file "$$BODY_FILE_PATH"

pr-review-clean:
	rm -rf $(PR_REVIEW_DIR)
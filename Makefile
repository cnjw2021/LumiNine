# Makefile
# ローカル開発環境用コマンド集
# 運用環境: Cloudflare Pages (frontend) + Cloud Run (backend) + Supabase (DB)

COMPOSE = docker compose

.PHONY: up down down-v stop restart rebuild logs help
.PHONY: build-be rebuild-be restart-be logs-be gen-pngs
.PHONY: build-fe rebuild-fe rebuild-fe-clean restart-fe logs-fe
.PHONY: test test-unit test-integration
.PHONY: db-seed db-init db-reset db-upgrade db-migrate db-downgrade db-stamp db-history db-current
.PHONY: pr-flow pr-flow-next pr-triage pr-triage-next pr-triage-manual pr-triage-manual-fix
.PHONY: pr-reply-batch pr-reply-batch-retry pr-reply-batch-manual pr-reply-batch-manual-force
.PHONY: pr-manual-flow pr-manual-fix-flow pr-followup pr-edit-meta pr-review-clean
.DEFAULT_GOAL := help

# PR リビュー自動化設定
PR_REVIEW_DIR ?= .pr-review
PR_BATCH_LIMIT ?= 5

# ==============================================================================
# 🐳 アプリケーション管理
# ==============================================================================
up: ## 🐳 ローカル開発環境を起動します。
	@echo "### ローカル開発環境を起動します... ###"
	$(COMPOSE) up -d --build --wait frontend backend

rebuild: ## 🔄 [注意] キャッシュなしで完全に再構築します。
	@echo "### キャッシュなしで再構築します... ###"
	$(COMPOSE) build --no-cache
	$(COMPOSE) up -d --wait frontend backend

down: ## ⛔️ コンテナを停止・削除します。
	@echo "### コンテナを停止します... ###"
	$(COMPOSE) down

down-v: ## 💥 [注意] コンテナとデータボリュームをすべて削除します。
	@echo "### コンテナを停止し、ボリュームを削除します... ###"
	$(COMPOSE) down -v

stop: ## ⛔️ 実行中のすべてのコンテナを停止します。
	@echo "### すべてのコンテナを停止します... ###"
	@if [ -n "$$(docker ps -q)" ]; then \
		docker stop $$(docker ps -q); \
	else \
		echo "実行中のコンテナはありません。"; \
	fi

restart: ## 🔄 サービスを再起動します。
	@echo "### サービスを再起動します... ###"
	$(COMPOSE) restart

# ==============================================================================
# 🔧 バックエンド専用管理
# ==============================================================================
build-be: ## 🔧 バックエンドのみをビルドします。
	@echo "### バックエンドのみをビルドします... ###"
	$(COMPOSE) build backend

rebuild-be: ## 🔄 バックエンドのみをキャッシュなしで再構築します。
	@echo "### バックエンドのみをキャッシュなしで再構築します... ###"
	$(COMPOSE) build --no-cache backend
	$(COMPOSE) up -d backend

restart-be: ## 🔄 バックエンドを再起動します。
	@echo "### バックエンドを再起動します... ###"
	$(COMPOSE) restart backend

gen-pngs: ## 🖼️ PDF用の九星盤PNGを事前生成します。
	@echo "### 九星盤PNGを事前生成します... ###"
	$(COMPOSE) run --rm backend python scripts/generate_main_star_pngs.py --size 900

logs-be: ## 📜 バックエンドの実時間ログを確認します。
	@echo "### バックエンド実時間ログを出力します... ###"
	$(COMPOSE) logs -f backend

# ==============================================================================
# 🎨 フロントエンド専用管理
# ==============================================================================
build-fe: ## 🎨 フロントエンドのみをビルドします。
	@echo "### フロントエンドのみをビルドします... ###"
	$(COMPOSE) build frontend

rebuild-fe: ## 🔄 フロントエンドのみをキャッシュなしで再構築します。
	@echo "### フロントエンドのみをキャッシュなしで再構築します... ###"
	$(COMPOSE) build --no-cache frontend
	$(COMPOSE) up -d frontend

rebuild-fe-clean: ## 🔄 フロントエンドを再構築し、匿名ボリュームも再作成します。(依存関係変更時)
	@echo "### フロントエンドをキャッシュなし＆ボリューム再作成で再構築します... ###"
	$(COMPOSE) build --no-cache frontend
	$(COMPOSE) up -d --renew-anon-volumes frontend

restart-fe: ## 🔄 フロントエンドのみを再起動します。
	@echo "### フロントエンドのみを再起動します... ###"
	$(COMPOSE) restart frontend

logs-fe: ## 📜 フロントエンドの実時間ログを確認します。
	@echo "### フロントエンド実時間ログを出力します... ###"
	$(COMPOSE) logs -f frontend

logs: ## 📜 全サービスの実時間ログを確認します。
	@echo "### 全サービスの実時間ログを出力します... ###"
	$(COMPOSE) logs -f

# ==============================================================================
# 🧪 テスト
# ==============================================================================
test: ## 🧪 Dockerコンテナ内でテストを実行します。
	@echo "### Dockerコンテナ内でテストを実行します... ###"
	$(COMPOSE) run --rm backend-test pytest

test-unit: ## 🧪 単体テストのみ実行します。(CI用: DB不要)
	@echo "### 単体テストのみ実行します... ###"
	$(COMPOSE) run --rm backend-test pytest --ignore=tests/golden_master --ignore=tests/test_direction_fortune_birthdate_2026.py -v

test-integration: ## 🧪 統合テストのみ実行します。(DB + バックエンドAPI必須)
	@echo "### 統合テストのみ実行します... ###"
	$(COMPOSE) run --rm backend-test pytest tests/golden_master tests/test_direction_fortune_birthdate_2026.py -v

# ==============================================================================
# 🔐 データベース管理
# ==============================================================================
db-seed: ## 🌱 データベースを完全にリセットし、Alembicマイグレーションで全データ（SQL + CSV）を再投入します。
	@echo "### データベースを完全にシード（Alembic 統合）します... ###"
	$(COMPOSE) run --rm backend-test python db_manage.py reset

db-init: ## ✅ [安全] Alembicマイグレーションを適用し、スーパーユーザーを作成します。
	@echo "### Alembicマイグレーションを適用します... ###"
	$(COMPOSE) run --rm backend python db_manage.py init

db-reset: ## 💥 [注意] DBを完全に初期化します。すべてのデータが削除されます。
	@echo "### データベースをリセットします! すべてのデータが削除されます... ###"
	$(COMPOSE) run --rm backend-test python db_manage.py reset

# --- 🔄 Alembic マイグレーション ---
db-upgrade: ## 🔄 マイグレーションを最新まで適用します。(flask db upgrade)
	@echo "### DB マイグレーション適用中... ###"
	cd backend && PYTHONPATH=. FLASK_APP=app.py flask db upgrade

db-migrate: ## 📝 モデル変更を検知して新しいマイグレーションを生成します。(使用法: make db-migrate MSG="説明")
	@if [ -z "$(MSG)" ]; then echo "使用法: make db-migrate MSG=\"マイグレーション説明\""; exit 1; fi
	@echo "### 新しいマイグレーション生成: $(MSG) ###"
	cd backend && PYTHONPATH=. FLASK_APP=app.py flask db migrate -m "$(MSG)"

db-downgrade: ## ⬇️ マイグレーションを1段階ロールバックします。(flask db downgrade)
	@echo "### DB マイグレーション1段階ロールバック中... ###"
	cd backend && PYTHONPATH=. FLASK_APP=app.py flask db downgrade

db-stamp: ## 🏷️ 既存DBに現在のマイグレーションバージョンをマーキングします。(使用法: make db-stamp REV=head)
	@if [ -z "$(REV)" ]; then echo "使用法: make db-stamp REV=head (またはリビジョンID)"; exit 1; fi
	@echo "### DBにマイグレーションバージョンマーキング: $(REV) ###"
	cd backend && PYTHONPATH=. FLASK_APP=app.py flask db stamp $(REV)

db-history: ## 📜 マイグレーション履歴を確認します。(flask db history)
	@cd backend && PYTHONPATH=. FLASK_APP=app.py flask db history

db-current: ## 📍 現在適用されているマイグレーションバージョンを確認します。(flask db current)
	@cd backend && PYTHONPATH=. FLASK_APP=app.py flask db current

# ==============================================================================
# 📝 PR リビュー自動化
# ==============================================================================
pr-flow: pr-triage
	@if [ -z "$(PR)" ]; then echo "使用法: make pr-flow PR=<番号> [BATCH=$(PR_BATCH_LIMIT)]"; exit 1; fi
	@echo ""
	@echo "=== PR リビュー自動化 次のステップ ==="
	@echo "生成ファイル:"
	@echo "  - $(PR_REVIEW_DIR)/pr-$(PR)-triage.md"
	@echo "  - $(PR_REVIEW_DIR)/pr-$(PR)-autofix-checklist.md"
	@echo "  - $(PR_REVIEW_DIR)/pr-$(PR)-reply-batch.json"
	@echo ""
	@AUTO_FIXABLE=$$(awk '/^- Auto-fixable:/ {print $$3; exit}' $(PR_REVIEW_DIR)/pr-$(PR)-triage.md 2>/dev/null || echo 0); \
	MANUAL=$$(awk '/^- Needs [Mm]anual [Vv]erification/ {print $$NF; exit}' $(PR_REVIEW_DIR)/pr-$(PR)-triage.md 2>/dev/null || echo 0); \
	DESIGN=$$(awk '/^- Needs design review:/ {print $$5; exit}' $(PR_REVIEW_DIR)/pr-$(PR)-triage.md 2>/dev/null || echo 0); \
	echo "権장順序:"; \
	echo "  1) triage 結果基準で修正/テスト/コミット/プッシュ"; \
	if [ "$$AUTO_FIXABLE" -gt 0 ]; then \
		echo "  2) make pr-reply-batch PR=$(PR)   # auto-fixable=$$AUTO_FIXABLE"; \
	fi; \
	if [ "$$MANUAL" -gt 0 ] || [ "$$DESIGN" -gt 0 ]; then \
		echo "  3) make pr-manual-flow PR=$(PR)   # manual+design=$$(($$MANUAL + $$DESIGN))"; \
	fi; \
	if [ "$$AUTO_FIXABLE" -eq 0 ] && [ "$$MANUAL" -eq 0 ] && [ "$$DESIGN" -eq 0 ]; then \
		echo "  2) reply/resolve 対象コメントがありません (0/0 予想)"; \
	fi; \
	echo "     (すでにhandledされたコメントに訂正replyが必要な場合: make pr-manual-fix-flow PR=$(PR))"

pr-flow-next: pr-triage-next
	@if [ -z "$(PR)" ]; then echo "使用法: make pr-flow-next PR=<番号> OFFSET=<数字> [BATCH=$(PR_BATCH_LIMIT)]"; exit 1; fi
	@if [ -z "$(OFFSET)" ]; then echo "使用法: make pr-flow-next PR=<番号> OFFSET=<数字> [BATCH=$(PR_BATCH_LIMIT)]"; exit 1; fi
	@echo ""
	@echo "=== PR リビュー自動化 次のバッチ案内 ==="
	@echo "バッチパラメータ:"
	@echo "  - OFFSET=$(OFFSET)"
	@echo "  - BATCH=$(or $(BATCH),$(PR_BATCH_LIMIT))"
	@echo "生成ファイル(同じパスに最新バッチ基準で更新):"
	@echo "  - $(PR_REVIEW_DIR)/pr-$(PR)-triage.md"
	@echo "  - $(PR_REVIEW_DIR)/pr-$(PR)-autofix-checklist.md"
	@echo "  - $(PR_REVIEW_DIR)/pr-$(PR)-reply-batch.json"
	@echo ""
	@AUTO_FIXABLE=$$(awk '/^- Auto-fixable included in this batch:/ {print $$7; exit}' $(PR_REVIEW_DIR)/pr-$(PR)-triage.md 2>/dev/null | cut -d'/' -f1); \
	AUTO_FIXABLE=$${AUTO_FIXABLE:-0}; \
	echo "権장順序:"; \
	echo "  1) 今回のバッチ(offset=$(OFFSET)) 項目修正/テスト/コミット/プッシュ"; \
	if [ "$$AUTO_FIXABLE" -gt 0 ]; then \
		echo "  2) make pr-reply-batch PR=$(PR)   # auto-fixable batch=$$AUTO_FIXABLE"; \
	else \
		echo "  2) auto-fixable バッチが空です。manual/design コメントなら make pr-manual-flow PR=$(PR) 使用"; \
	fi

pr-triage:
	@if [ -z "$(PR)" ]; then echo "使用法: make pr-triage PR=<番号> [BATCH=$(PR_BATCH_LIMIT)]"; exit 1; fi
	npm run pr:triage -- $(PR) \
	  --limit-auto-fix $(or $(BATCH),$(PR_BATCH_LIMIT)) \
	  --emit-reply-batch \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-triage-next:
	@if [ -z "$(PR)" ]; then echo "使用法: make pr-triage-next PR=<番号> OFFSET=<数字> [BATCH=$(PR_BATCH_LIMIT)]"; exit 1; fi
	@if [ -z "$(OFFSET)" ]; then echo "使用法: make pr-triage-next PR=<番号> OFFSET=<数字> [BATCH=$(PR_BATCH_LIMIT)]"; exit 1; fi
	npm run pr:triage -- $(PR) \
	  --offset-auto-fix $(OFFSET) \
	  --limit-auto-fix $(or $(BATCH),$(PR_BATCH_LIMIT)) \
	  --emit-reply-batch \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-triage-manual:
	@if [ -z "$(PR)" ]; then echo "使用法: make pr-triage-manual PR=<番号> [BATCH=$(PR_BATCH_LIMIT)] [OFFSET=<数字>]"; exit 1; fi
	npm run pr:triage -- $(PR) \
	  $(if $(OFFSET),--offset-auto-fix $(OFFSET),) \
	  --limit-auto-fix $(or $(BATCH),$(PR_BATCH_LIMIT)) \
	  --emit-manual-reply-batch \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-triage-manual-fix:
	@if [ -z "$(PR)" ]; then echo "使用法: make pr-triage-manual-fix PR=<番号> [BATCH=$(PR_BATCH_LIMIT)] [OFFSET=<数字>]"; exit 1; fi
	npm run pr:triage -- $(PR) \
	  $(if $(OFFSET),--offset-auto-fix $(OFFSET),) \
	  --limit-auto-fix $(or $(BATCH),$(PR_BATCH_LIMIT)) \
	  --emit-manual-reply-batch \
	  --include-resolved \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-reply-batch:
	@if [ -z "$(PR)" ]; then echo "使用法: make pr-reply-batch PR=<番号>"; exit 1; fi
	npm run pr:review-reply -- \
	  --batch-file $(PR_REVIEW_DIR)/pr-$(PR)-reply-batch.json \
	  --continue-on-error \
	  --failed-batch-out $(PR_REVIEW_DIR)/pr-$(PR)-reply-batch.failed.json \
	  --log-file $(PR_REVIEW_DIR)/reply-actions.ndjson \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-reply-batch-retry:
	@if [ -z "$(PR)" ]; then echo "使用法: make pr-reply-batch-retry PR=<番号>"; exit 1; fi
	npm run pr:review-reply -- \
	  --batch-file $(PR_REVIEW_DIR)/pr-$(PR)-reply-batch.failed.json \
	  --continue-on-error \
	  --failed-batch-out $(PR_REVIEW_DIR)/pr-$(PR)-reply-batch.failed.next.json \
	  --log-file $(PR_REVIEW_DIR)/reply-actions.ndjson \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-reply-batch-manual:
	@if [ -z "$(PR)" ]; then echo "使用法: make pr-reply-batch-manual PR=<番号>"; exit 1; fi
	@if [ ! -f "$(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.json" ]; then \
		echo "manual reply batch ファイルがありません: $(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.json"; \
		echo "先に実行: make pr-triage-manual PR=$(PR)"; \
		echo "すでにhandledされたコメント訂正replyが目的なら: make pr-triage-manual-fix PR=$(PR)"; \
		exit 1; \
	fi
	npm run pr:review-reply -- \
	  --batch-file $(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.json \
	  --continue-on-error \
	  --failed-batch-out $(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.failed.json \
	  --log-file $(PR_REVIEW_DIR)/reply-actions.ndjson \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-reply-batch-manual-force:
	@if [ -z "$(PR)" ]; then echo "使用法: make pr-reply-batch-manual-force PR=<番号>"; exit 1; fi
	@if [ ! -f "$(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.json" ]; then \
		echo "manual reply batch ファイルがありません: $(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.json"; \
		echo "先に実行: make pr-triage-manual-fix PR=$(PR)"; \
		exit 1; \
	fi
	npm run pr:review-reply -- \
	  --batch-file $(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.json \
	  --continue-on-error \
	  --failed-batch-out $(PR_REVIEW_DIR)/pr-$(PR)-manual-reply-batch.failed.json \
	  --log-file $(PR_REVIEW_DIR)/reply-actions.ndjson \
	  --handled-urls $(PR_REVIEW_DIR)/handled_comment_urls.json

pr-manual-flow: pr-triage-manual pr-reply-batch-manual
	@if [ -z "$(PR)" ]; then echo "使用法: make pr-manual-flow PR=<番号> [BATCH=$(PR_BATCH_LIMIT)] [OFFSET=<数字>]"; exit 1; fi
	@echo ""
	@echo "=== Manual(review + design-review) reply 処理完了 ==="
	@echo "実行項目:"
	@echo "  1) make pr-triage-manual PR=$(PR) $(if $(OFFSET),OFFSET=$(OFFSET),) $(if $(BATCH),BATCH=$(BATCH),)"
	@echo "  2) make pr-reply-batch-manual PR=$(PR)"

pr-manual-fix-flow: pr-triage-manual-fix pr-reply-batch-manual-force
	@if [ -z "$(PR)" ]; then echo "使用法: make pr-manual-fix-flow PR=<番号> [BATCH=$(PR_BATCH_LIMIT)] [OFFSET=<数字>]"; exit 1; fi
	@echo ""
	@echo "=== Manual 訂正 reply 処理完了 ==="
	@echo "実行項目:"
	@echo "  1) make pr-triage-manual-fix PR=$(PR) $(if $(OFFSET),OFFSET=$(OFFSET),) $(if $(BATCH),BATCH=$(BATCH),)"
	@echo "  2) make pr-reply-batch-manual-force PR=$(PR)"

pr-followup: pr-triage
	@if [ -z "$(PR)" ]; then echo "使用法: make pr-followup PR=<番号> [BATCH=$(PR_BATCH_LIMIT)] [OFFSET=<数字>]"; exit 1; fi
	@AUTO_FIXABLE=$$(awk '/^- Auto-fixable:/ {print $$3; exit}' $(PR_REVIEW_DIR)/pr-$(PR)-triage.md 2>/dev/null || echo 0); \
	MANUAL=$$(awk '/^- Needs [Mm]anual [Vv]erification/ {print $$NF; exit}' $(PR_REVIEW_DIR)/pr-$(PR)-triage.md 2>/dev/null || echo 0); \
	DESIGN=$$(awk '/^- Needs design review:/ {print $$5; exit}' $(PR_REVIEW_DIR)/pr-$(PR)-triage.md 2>/dev/null || echo 0); \
	if [ "$$AUTO_FIXABLE" -gt 0 ]; then \
		echo "=== Auto-fixable reply/resolve バッチ実行 ==="; \
		$(MAKE) pr-reply-batch PR=$(PR); \
	else \
		echo "=== Auto-fixable reply/resolve 対象なし ==="; \
	fi; \
	if [ "$$MANUAL" -gt 0 ] || [ "$$DESIGN" -gt 0 ]; then \
		echo "=== Manual/Design-review reply/resolve バッチ実行 ==="; \
		$(MAKE) pr-manual-flow PR=$(PR) $(if $(OFFSET),OFFSET=$(OFFSET),) $(if $(BATCH),BATCH=$(BATCH),); \
	else \
		echo "=== Manual/Design-review reply/resolve 対象なし ==="; \
	fi
	@echo ""
	@echo "=== PR フォローアップ処理案内 (繰り返し作業完了) ==="
	@echo "完了:"
	@echo "  - triage 実行"
	@echo "  - auto-fixable reply/resolve バッチ実行 (ある場合)"
	@echo "  - manual/design reply/resolve バッチ実行 (ある場合)"
	@echo ""
	@echo "次のステップ(順序重要):"
	@echo "  1) 修正/テスト/コミット/プッシュが追加であった場合 PR タイトル/本文更新"
	@echo "  2) (auto/manual 混合含む) すべての reply/resolve 反映後 Copilot リビュー再要求"
	@echo "     - 現在のPRでCopilotリビューが既に完了している場合skip"

pr-edit-meta:
	@if [ -z "$(PR)" ]; then echo "使用法: make pr-edit-meta PR=<番号> [TITLE=\"タイトル\"] [BODY_FILE=/tmp/pr<番号>_body.md] [TITLE_FILE=/tmp/pr<番号>_title.txt]"; exit 1; fi
	@BODY_FILE_PATH="$(if $(BODY_FILE),$(BODY_FILE),/tmp/pr$(PR)_body.md)"; \
	TITLE_FILE_PATH="$(if $(TITLE_FILE),$(TITLE_FILE),/tmp/pr$(PR)_title.txt)"; \
	TITLE_VALUE="$(TITLE)"; \
	if [ -z "$$TITLE_VALUE" ]; then \
		if [ ! -f "$$TITLE_FILE_PATH" ]; then \
			echo "TITLE 未指定でタイトルファイルもありません: $$TITLE_FILE_PATH"; \
			echo "使用法: make pr-edit-meta PR=$(PR) TITLE=\"タイトル\""; \
			exit 1; \
		fi; \
		TITLE_VALUE="$$(cat "$$TITLE_FILE_PATH")"; \
	fi; \
	if [ ! -f "$$BODY_FILE_PATH" ]; then \
		echo "本文ファイルがありません: $$BODY_FILE_PATH"; \
		echo "例: /tmp/pr$(PR)_body.md"; \
		exit 1; \
	fi; \
	echo "=== GH 認証状態確認 ==="; \
	gh auth status || true; \
	echo ""; \
	echo "=== PR #$(PR) タイトル/本文更新 ==="; \
	echo "Title: $$TITLE_VALUE"; \
	echo "Body : $$BODY_FILE_PATH"; \
	gh pr edit $(PR) --title "$$TITLE_VALUE" --body-file "$$BODY_FILE_PATH"

pr-review-clean:
	rm -rf $(PR_REVIEW_DIR)

# ==============================================================================
# ℹ️ ヘルプ
# ==============================================================================
help: ## ℹ️ 使用可能なすべてのコマンドを表示します。
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
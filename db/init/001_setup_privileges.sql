-- PostgreSQL: MySQL 001_create_users.sql の代替
-- PostgreSQL では GRANT はスーパーユーザーレベルで管理するため、
-- Docker 初期化時の権限設定は docker-compose.dev.yml の POSTGRES_USER で自動対応済み。
-- このファイルは互換性のためプレースホルダーとして残す。

-- (no-op: PostgreSQL Docker image uses POSTGRES_USER with full access by default)
SELECT 1;

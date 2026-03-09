"""initial schema

Revision ID: 001
Revises: 
Create Date: 2026-03-09

既存の 000_create_tables.sql を実行してスキーマを作成します。
既にテーブルが存在する場合は何もしません (CREATE TABLE IF NOT EXISTS)。

SQL ファイルの検索パス:
  1. backend/db/init/ (Docker コンテナ内)
  2. db/init/ (リポジトリルートからの相対パス — CI/ローカル)
"""
from alembic import op
import sqlalchemy as sa
import os

# revision identifiers
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def _find_sql_file(filename):
    """SQL ファイルをコンテナ内 / リポジトリルートの両方から検索"""
    candidates = [
        # Docker コンテナ内: /app/db/init/
        os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'init', filename),
        # リポジトリルート (CI / ローカル): ../../.. → repo root → db/init/
        os.path.join(os.path.dirname(__file__), '..', '..', '..', 'db', 'init', filename),
    ]
    for path in candidates:
        resolved = os.path.normpath(path)
        if os.path.exists(resolved):
            return resolved
    raise FileNotFoundError(
        f"SQL file '{filename}' not found. Searched: {[os.path.normpath(c) for c in candidates]}"
    )


def upgrade():
    sql_path = _find_sql_file('000_create_tables.sql')
    with open(sql_path, 'r') as f:
        sql = f.read()
    op.execute(sa.text(sql))


def downgrade():
    # 全テーブルを逆順で削除 (データ損失注意)
    tables = [
        'recommendation_history', 'user_permissions', 'admin_account_limit',
        'powerstone_master', 'pattern_switch_dates',
        'hourly_star_zodiacs', 'zodiac_group_members', 'zodiac_groups',
        'monthly_directions', 'star_groups', 'star_grid_patterns',
        'star_attributes', 'daily_astrology', 'solar_terms', 'solar_starts',
        'stars', 'users', 'permissions', 'system_config',
    ]
    for t in tables:
        op.execute(sa.text(f'DROP TABLE IF EXISTS {t} CASCADE'))

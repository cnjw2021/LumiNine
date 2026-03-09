"""initial schema

Revision ID: 001
Revises: 
Create Date: 2026-03-09

既存の 000_create_tables.sql を実行してスキーマを作成します。
既にテーブルが存在する場合は何もしません (CREATE TABLE IF NOT EXISTS)。

マイグレーションは CI (GitHub Actions) またはローカル環境でのみ実行されます。
Docker コンテナ内では実行されません (start.sh は gunicorn のみ起動)。
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
    """SQL ファイルを CI / ローカル環境から検索"""
    candidates = [
        # backend/ 直下に db/init/ がある場合 (将来の構成変更に備えて)
        os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'init', filename),
        # リポジトリルート (CI / ローカル): versions/ → migrations/ → backend/ → repo root → db/init/
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

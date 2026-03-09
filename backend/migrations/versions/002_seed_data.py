"""seed data and superuser

Revision ID: 002
Revises: 001_initial_schema
Create Date: 2026-03-09

シードデータ（星データ、属性、方位、パワーストーン等）挿入とスーパーユーザー作成。
db/init/ 内の SQL ファイルを順番に実行 + SQL でスーパーユーザー作成。
全て冪等 (ON CONFLICT DO NOTHING / IF NOT EXISTS)。
"""
from alembic import op
import sqlalchemy as sa
import os

# revision identifiers
revision = '002_seed_data'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None

# シード SQL ファイル (実行順)
_SEED_FILES = [
    '100_stars.sql',
    '200_star_attributes.sql',
    '210_star_grid_patterns.sql',
    '300_monthly_directions.sql',
    '310_star_number_group.sql',
    '320_pattern_switch_dates.sql',
    '510_powerstone_seed.sql',
    '900_system_data.sql',
]


def upgrade():
    # ── 1. SQL シードデータ ──────────────────────────────────────
    db_init_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'init')
    for sql_file in _SEED_FILES:
        sql_path = os.path.join(db_init_dir, sql_file)
        if os.path.exists(sql_path):
            with open(sql_path, 'r') as f:
                sql = f.read()
            op.execute(sa.text(sql))

    # ── 2. スーパーユーザー作成 (bcrypt ハッシュ) ────────────────────
    _create_superuser()

    # ── 3. スーパーユーザーに全権限付与 ─────────────────────────────
    _assign_superuser_permissions()


def _create_superuser():
    """環境変数からスーパーユーザーを作成 (冪等)"""
    email = os.environ.get('SUPERUSER_EMAIL')
    password = os.environ.get('SUPERUSER_PASSWORD')

    if not email or not password:
        print("SUPERUSER env vars not set — skipping superuser creation")
        return

    # 既に存在するかチェック
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM users WHERE email = :email"), {"email": email})
    if result.fetchone():
        print(f"Superuser '{email}' already exists — skipping creation")
        return

    # bcrypt でパスワードハッシュ化
    import bcrypt
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn.execute(
        sa.text(
            "INSERT INTO users (name, email, password, is_active, is_admin, is_superuser, is_deleted) "
            "VALUES ('Super User', :email, :password, true, true, true, false) "
            "ON CONFLICT (email) DO NOTHING"
        ),
        {"email": email, "password": hashed}
    )
    print(f"Superuser '{email}' created")


def _assign_superuser_permissions():
    """スーパーユーザーに全権限を付与 (冪等)"""
    email = os.environ.get('SUPERUSER_EMAIL')
    if not email:
        return

    conn = op.get_bind()
    conn.execute(
        sa.text(
            "INSERT INTO user_permissions (user_id, permission_id) "
            "SELECT u.id, p.id FROM users u CROSS JOIN permissions p "
            "WHERE u.email = :email "
            "ON CONFLICT DO NOTHING"
        ),
        {"email": email}
    )
    print(f"Assigned all permissions to superuser '{email}'")


def downgrade():
    # シードデータの削除は危険なので空実装
    pass

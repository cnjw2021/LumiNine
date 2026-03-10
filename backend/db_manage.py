import os
import sys
import argparse
from flask import Flask
from sqlalchemy import text

import psycopg2

from core.database import db
from core.db_config import get_postgres_connection
from core.utils.logger import get_logger

logger = get_logger(__name__)

def create_app():
    """Flask アプリケーションインスタンスを作成して設定します。"""
    app = Flask(__name__)
    
    # 環境変数からデータベース URIを構成
    db_uri = os.environ.get('DATABASE_URL') or \
        f"postgresql+psycopg2://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}"
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def create_superuser():
    """環境変数を使用してスーパーユーザーを作成し、全権限を付与します。"""
    logger.info("スーパーユーザーの作成を開始します...")
    app = create_app()
    with app.app_context():
        try:
            from apps.reading.shared.domain.entities.user import User
            from apps.reading.shared.domain.entities.permission import Permission
            from apps.reading.shared.domain.entities.user_permission import UserPermission

            email = os.environ.get('SUPERUSER_EMAIL')
            password = os.environ.get('SUPERUSER_PASSWORD')

            if not email or not password:
                logger.warning("SUPERUSER 環境変数が設定されていません。スーパーユーザーの作成をスキップします。")
                return

            superuser = User.query.filter_by(email=email).first()
            if superuser:
                logger.info(f"スーパーユーザー '{email}'は既に存在します。")
            else:
                # User モデルを通して作成すると、モデル内部のパスワードハッシュリグが自動的に適用されます。
                superuser = User(
                    name='Super User',
                    email=email,
                    password=password,
                    is_admin=True,
                    is_superuser=True
                )
                db.session.add(superuser)
                db.session.commit()
                logger.info(f"スーパーユーザー '{email}'が成功して作成されました。")

            # ── 全権限を付与 (冪等) ──────────────────────────────────
            all_permissions = Permission.query.all()
            if all_permissions:
                assigned = 0
                for perm in all_permissions:
                    exists = UserPermission.query.filter_by(
                        user_id=superuser.id, permission_id=perm.id
                    ).first()
                    if not exists:
                        db.session.add(UserPermission(
                            user_id=superuser.id, permission_id=perm.id
                        ))
                        assigned += 1
                if assigned > 0:
                    db.session.commit()
                    logger.info(f"スーパーユーザーに {assigned} 件の権限を付与しました。")
                else:
                    logger.info("スーパーユーザーの権限は既に全て付与済みです。")
            else:
                logger.warning("permissions テーブルにデータがありません。権限付与をスキップします。")

        except Exception as e:
            logger.error(f"スーパーユーザー作成中にエラーが発生しました: {e}")
            db.session.rollback()
            raise


def _run_alembic_upgrade():
    """Alembic マイグレーションを最新版まで適用します。"""
    import subprocess
    logger.info("Alembic マイグレーション適用中...")
    result = subprocess.run(
        ["flask", "db", "upgrade"],
        env={**os.environ, "PYTHONPATH": os.path.dirname(__file__), "FLASK_APP": "app.py"},
        cwd=os.path.dirname(__file__) or ".",
        capture_output=True,
        text=True,
    )
    if result.stdout:
        logger.info(result.stdout.strip())
    if result.stderr:
        log_fn = logger.error if result.returncode != 0 else logger.warning
        log_fn("Alembic stderr: %s", result.stderr.strip())
    if result.returncode != 0:
        raise RuntimeError(
            f"flask db upgrade failed (exit {result.returncode})\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    logger.info("Alembic マイグレーション適用完了。")


def run_init():
    """
    Alembic マイグレーションを適用し、スーパーユーザーを作成します。
    Alembic が DDL (001) + SQL シード (002) + CSV シード (003) を一括で処理するため、
    db_manage.py は 'flask db upgrade' の実行とスーパーユーザー作成のみを担当します。
    """
    logger.info("DB init script started...")
    _run_alembic_upgrade()
    create_superuser()
    logger.info("DB init script finished.")

def run_reset():
    """
    すべてのテーブルを削除し、Alembic マイグレーションで再構築します。
    """
    logger.warning("DB RESET 開始! すべてのデータが削除されます。")
    conn = get_postgres_connection()
    conn.autocommit = False
    cursor = conn.cursor()

    try:
        # すべてのテーブルを削除 (CASCADE で依存関係も一括削除)
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        for table in tables:
            cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
        conn.commit()
        logger.info("すべてのテーブルが削除されました。")
    finally:
        cursor.close()
        conn.close()

    # Alembic で再構築 (DDL + SQL シード + CSV シード)
    _run_alembic_upgrade()

    # SQLAlchemyを通してスーパーユーザーを作成 (パスワードハッシュが保証されます)
    create_superuser()
    
    logger.info("DB リセットが完了しました。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="データベース管理スクリプト")
    parser.add_argument(
        "command",
        choices=["init", "reset", "create-superuser"],
        help="実行するコマンド: 'init' (Alembic適用+スーパーユーザー), 'reset' (全削除+再構築), 'create-superuser' (スーパーユーザーのみ作成)"
    )
    args = parser.parse_args()

    try:
        if args.command == "init":
            run_init()
        elif args.command == "reset":
            run_reset()
        elif args.command == "create-superuser":
            create_superuser()
    except Exception as e:
        logger.error(f"スクリプト実行中にエラーが発生しました: {e}", exc_info=True)
        sys.exit(1)
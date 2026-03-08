import os
import sys
import traceback
import argparse
from flask import Flask
from sqlalchemy import text
from mysql.connector import Error

from core.database import db
from core.db_config import get_mysql_connection
from core.utils.logger import get_logger
from scripts.csv_file_loader import load_all_csv_data

logger = get_logger(__name__)

def create_app():
    """Flask アプリケーションインスタンスを作成して設定します。"""
    app = Flask(__name__)
    
    # 環境変数からデータベース URIを構成
    db_uri = os.environ.get('DATABASE_URL') or \
        f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}?charset=utf8mb4"
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def create_superuser():
    """環境変数を使用してスーパーユーザーを作成します。 (モデルのハッシュリグが適用されます)"""
    logger.info("スーパーユーザーの作成を開始します...")
    app = create_app()
    with app.app_context():
        try:
            from apps.fortunetelling.shared.domain.entities.user import User
            email = os.environ.get('SUPERUSER_EMAIL')
            password = os.environ.get('SUPERUSER_PASSWORD')

            if not email or not password:
                logger.warning("SUPERUSER 環境変数が設定されていません。スーパーユーザーの作成をスキップします。")
                return

            if User.query.filter_by(email=email).first():
                logger.info(f"スーパーユーザー '{email}'は既に存在します。")
                return
            
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
        except Exception as e:
            logger.error(f"スーパーユーザー作成中にエラーが発生しました: {e}")
            db.session.rollback()
            raise

def execute_sql_file(cursor, file_path):
    """指定されたSQLファイルを実行します。"""
    if not os.path.exists(file_path):
        logger.error(f"SQLファイル '{file_path}'を見つけることができません。")
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
            for result in cursor.execute(sql_content, multi=True):
                pass
        logger.info(f"SQLファイル '{os.path.basename(file_path)}'が成功して実行されました。")
    except Error as e:
        logger.error(f"SQLファイル '{file_path}'実行中にエラーが発生しました: {e}")
        raise


# SQLシードファイルとそのファイルが挿入するテーブルのマッピング
# target_tables 指定時に不要なファイルの実行をスキップするために使用
_SQL_SEED_FILE_TABLE_MAP = {
    '100_stars.sql': {'stars'},

    '210_star_grid_patterns.sql': {'star_grid_patterns'},
    '300_monthly_directions.sql': {'monthly_directions'},
    '310_star_number_group.sql': {'star_groups'},
    '320_pattern_switch_dates.sql': {'pattern_switch_dates'},

    '510_powerstone_seed.sql': {'powerstone_master'},
    '900_system_data.sql': {'system_config', 'admin_account_limit', 'permissions'},
}


def seed_database(cursor, target_tables=None):
    """SQL および CSV ファイルで初期データを埋め込みます。
    target_tables が指定された場合は、該当するテーブルに関連するSQLファイルとCSVデータのみをロードします。
    """
    logger.info(f"データシードを開始します... {'(Target: ' + ', '.join(target_tables) + ')' if target_tables else '(All)'}")

    for sql_file, tables in _SQL_SEED_FILE_TABLE_MAP.items():
        # target_tables が指定されている場合、対象テーブルに関連するファイルのみ実行
        if target_tables and not tables & target_tables:
            logger.debug("スキップ: %s (対象テーブルに該当なし)", sql_file)
            continue
        sql_file_path = os.path.join('mysql', 'init', sql_file)
        execute_sql_file(cursor, sql_file_path)

    logger.info("CSV データをロードします...")
    load_all_csv_data(target_tables=target_tables)
    logger.info("データシードが完了しました。")

def _get_existing_tables(cursor) -> set:
    """現在のデータベースに存在するテーブル名の集合を返します。"""
    cursor.execute("SHOW TABLES")
    return {row[0] for row in cursor.fetchall()}

# 000_create_tables.sql およびシードSQLファイルに定義されている全テーブルのリスト
# 新しいテーブルを追加した場合はここにも追加してください
_EXPECTED_TABLES = {
    'stars', 'solar_starts', 'solar_terms', 'daily_astrology',
    'star_groups',
    'star_grid_patterns', 'monthly_directions',
    'zodiac_groups', 'zodiac_group_members',
    'hourly_star_zodiacs', 'system_config', 'admin_account_limit',
    'permissions', 'users', 'user_permissions',
    'powerstone_master', 'recommendation_history',
    # シードSQL内で CREATE TABLE IF NOT EXISTS されるテーブル
    'pattern_switch_dates',
}

def run_init():
    """
    [役割 変更]
    DB 初期化はMySQL コンテナが担当しますが、ボリュームの問題等でテーブルがない場合は
    安全のためにテーブル作成と初期データシードを実行します。
    既存DBで一部テーブルが不足している場合は、DDL (CREATE TABLE IF NOT EXISTS) と
    シードを増分適用します。その後、スーパーユーザー作成を担当します。
    """
    logger.info("DB init script started: Checking database state...")
    
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    existing = _get_existing_tables(cursor)

    if not existing:
        # 完全初期化: テーブルもデータもない
        logger.warning("テーブルが存在しません。テーブルの作成とデータのシードを開始します...")
        execute_sql_file(cursor, os.path.join('mysql', 'init', '000_create_tables.sql'))
        seed_database(cursor)
        conn.commit()
    else:
        missing = _EXPECTED_TABLES - existing
        if missing:
            # 増分適用: 既存DBに不足テーブルがある場合
            logger.warning("不足テーブル検出: %s — DDL+シードを増分適用します。", missing)
            execute_sql_file(cursor, os.path.join('mysql', 'init', '000_create_tables.sql'))
            # 不足しているテーブルのみをターゲットにシードを実行
            seed_database(cursor, target_tables=missing)
            conn.commit()
        else:
            logger.info("テーブルは既に存在します。データシードはスキップします。")
        
    cursor.close()
    conn.close()

    # テーブル 存在 関係なく、スーパーユーザーが存在しない場合は常に作成しようとします
    # create_superuser 関数 内部に既存 存在 チェック ロジックがあります
    create_superuser()
    logger.info("DB init script finished.")

def run_reset():
    """
    すべてのテーブルを削除し、新規に作成した後、データを再度埋め込み、スーパーユーザーを作成します。
    """
    logger.warning("DB RESET 開始! すべてのデータが削除されます。")
    conn = get_mysql_connection()
    cursor = conn.cursor()

    # すべてのテーブルを削除
    cursor.execute("SET FOREIGN_key_CHECKS=0")
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
    cursor.execute("SET FOREIGN_key_CHECKS=1")
    logger.info("すべてのテーブルが削除されました。")

    # テーブル 再作成 及び データ シード (MySQL initdb.dと同じロジックを実行)
    execute_sql_file(cursor, os.path.join('mysql', 'init', '000_create_tables.sql'))
    conn.commit()  # CSV loader uses a separate connection, so tables must be committed first
    seed_database(cursor) # SQL 及び CSV データ
    
    conn.commit()
    cursor.close()
    conn.close()

    # SQLAlchemyを通してスーパーユーザーを作成 (パスワードハッシュが保証されます)
    create_superuser()
    
    logger.info("DB リセットが完了しました。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="データベース管理スクリプト")
    parser.add_argument("command", choices=["init", "reset"], help="実行するコマンド: 'init' (安全な初期化), 'reset' (すべてのデータを削除して再構成)")
    args = parser.parse_args()

    try:
        if args.command == "init":
            run_init()
        elif args.command == "reset":
            run_reset()
    except Exception as e:
        logger.error(f"スクリプト実行中にエラーが発生しました: {e}", exc_info=True)
        sys.exit(1)
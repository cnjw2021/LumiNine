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
            from apps.ninestarki.domain.entities.user import User
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

def check_if_tables_exist(cursor):
    """テーブルが1つでも存在するかどうかを確認します。"""
    try:
        cursor.execute("SHOW TABLES")
        return len(cursor.fetchall()) > 0
    except Exception:
        return False

def seed_database(cursor):
    """SQL および CSV ファイルで初期データを埋め込みます。"""
    logger.info("データシードを開始します...")
    
    data_sql_files = [
        '100_stars.sql', '103_stellar_cycles.sql', '200_star_attributes.sql',
        '210_star_grid_patterns.sql', '300_monthly_directions.sql',
        '310_star_number_group.sql', '320_pattern_switch_dates.sql',
        '400_monthly_star_readings.sql', '410_daily_star_readings.sql',
        '900_system_data.sql',
    ]
    
    for sql_file in data_sql_files:
        sql_file_path = os.path.join('mysql', 'init', sql_file)
        execute_sql_file(cursor, sql_file_path)

    logger.info("CSV データをロードします...")
    load_all_csv_data()
    logger.info("データシードが完了しました。")

def run_init():
    """
    [役割 変更]
    DB 初期化はMySQL コンテナが担当しますが、ボリュームの問題等でテーブルがない場合は
    安全のためにテーブル作成と初期データシードを実行します。その後、スーパーユーザー作成を担当します。
    """
    logger.info("DB init script started: Checking database state...")
    
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    if not check_if_tables_exist(cursor):
        logger.warning("テーブルが存在しません。テーブルの作成とデータのシードを開始します...")
        execute_sql_file(cursor, os.path.join('mysql', 'init', '000_create_tables.sql'))
        seed_database(cursor) # SQL 及び CSV データ
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
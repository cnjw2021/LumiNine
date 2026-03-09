import os
import time
import pandas as pd
import psycopg2
from core.utils.logger import get_logger
from core.db_config import get_postgres_connection, get_db_connection_info

# ロガーの初期化
logger = get_logger(__name__)

BASE_CSV_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'csv')

def get_csv_path(filename, base_dir=None):
    """CSVファイルの正しいパスを取得する"""
    if base_dir is None:
        base_dir = BASE_CSV_DIR
    
    # 絶対パスの場合はそのまま返す
    if os.path.isabs(filename):
        return filename
        
    # 相対パスの場合はbase_dirからの相対パスとして扱う
    return os.path.join(base_dir, filename)

def load_csv_to_table(connection, csv_filename, table_name, column_mapping=None, truncate_table=True):
    """CSVファイルからPostgreSQLテーブルにデータをロードする（connectionは必須・先頭）
    
    PostgreSQL版ではCOPYコマンドを使用して高速ローディングを行います。
    """
    csv_path = get_csv_path(csv_filename)
    if not os.path.exists(csv_path):
        logger.error(f"CSVファイル {csv_path} が見つかりません")
        return 0
    row_count = 0
    try:
        cursor = connection.cursor()
        if truncate_table:
            logger.info(f"{table_name}テーブルの既存データを削除します...")
            cursor.execute(f"DELETE FROM {table_name}")
            connection.commit()
        start_time = time.time()
        
        # PostgreSQL COPY コマンドで高速ローディング
        try:
            if column_mapping:
                columns = list(column_mapping.values())
            else:
                df_header = pd.read_csv(csv_path, nrows=0)
                columns = df_header.columns.tolist()
            
            # created_at, updated_at はCSVに含まれないため除外してCOPY
            copy_columns = [c for c in columns if c not in ('created_at', 'updated_at')]
            
            columns_str = ', '.join(copy_columns)
            logger.info(f"COPY {table_name} ({columns_str}) FROM {csv_path}")
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                cursor.copy_expert(
                    f"COPY {table_name} ({columns_str}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)",
                    f
                )
            connection.commit()
            
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
        except psycopg2.Error as e:
            logger.error(f"COPYで失敗しました: {e}")
            connection.rollback()
            raise
            
        end_time = time.time()
        logger.info(f"{table_name}のロード完了: {row_count}行 {end_time-start_time:.2f}秒")
    except Exception as e:
        logger.error(f"CSVデータロード中にエラーが発生しました: {e}")
        raise
    return row_count

def load_multiple_csv_files(connection, csv_table_mapping, truncate_tables=True):
    """複数のCSVファイルをロードする（connectionは必須・先頭）"""
    results = {}
    try:
        for csv_file, table_info in csv_table_mapping.items():
            if isinstance(table_info, str):
                table_name = table_info
                column_mapping = None
            else:
                table_name = table_info.get('table')
                column_mapping = table_info.get('columns')
            row_count = load_csv_to_table(
                connection,
                csv_file, 
                table_name,
                column_mapping=column_mapping,
                truncate_table=truncate_tables
            )
            results[table_name] = row_count
    finally:
        if connection is not None:
            try:
                connection.close()
                logger.debug("共有データベース接続を閉じました")
            except Exception:
                pass
    return results
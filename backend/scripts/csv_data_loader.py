import os
import time
import pandas as pd
from mysql.connector import Error
from core.utils.logger import get_logger
from core.db_config import get_mysql_connection, get_db_connection_info

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

def load_csv_to_table(connection, csv_filename, table_name, column_mapping=None, truncate_table=True, use_load_data_infile=True):
    """CSVファイルからMySQLテーブルにデータをロードする（connectionは必須・先頭）"""
    csv_path = get_csv_path(csv_filename)
    if not os.path.exists(csv_path):
        logger.error(f"CSVファイル {csv_path} が見つかりません")
        return 0
    row_count = 0
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            if truncate_table:
                logger.info(f"{table_name}テーブルの既存データを削除します...")
                cursor.execute(f"DELETE FROM {table_name}")
                connection.commit()
            start_time = time.time()
            if use_load_data_infile:
                try:
                    if column_mapping:
                        columns = column_mapping.values()
                    else:
                        df_header = pd.read_csv(csv_path, nrows=0)
                        columns = df_header.columns.tolist()
                    mysql_file_path = csv_path
                    if '/app/data/' in csv_path:
                        mysql_file_path = csv_path.replace('/app/data/', '/var/lib/mysql-files/')
                    logger.info(f"LOAD DATA : {mysql_file_path}")
                    load_query = f"""
                    LOAD DATA INFILE '{mysql_file_path}'
                    INTO TABLE {table_name}
                    FIELDS TERMINATED BY ',' 
                    OPTIONALLY ENCLOSED BY '"'
                    LINES TERMINATED BY '\\n'
                    IGNORE 1 LINES
                    ({', '.join(columns)})
                    """
                    if 'created_at' in columns or 'updated_at' in columns:
                        load_query += "\nSET "
                        if 'created_at' in columns:
                            load_query += "created_at = NOW()"
                        if 'created_at' in columns and 'updated_at' in columns:
                            load_query += ", "
                        if 'updated_at' in columns:
                            load_query += "updated_at = NOW()"
                    cursor.execute(load_query)
                    connection.commit()
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                except Error as e:
                    logger.error(f"LOAD DATA INFILEで失敗しました: {e}")
                    use_load_data_infile = False
            end_time = time.time()
            logger.info(f"{table_name}のロード完了: {row_count}行 {end_time-start_time:.2f}秒")
    except Exception as e:
        logger.error(f"CSVデータロード中にエラーが発生しました: {e}")
        raise
    return row_count

def load_multiple_csv_files(connection, csv_table_mapping, truncate_tables=True, use_load_data_infile=True):
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
                truncate_table=truncate_tables,
                use_load_data_infile=use_load_data_infile
            )
            results[table_name] = row_count
    finally:
        if connection is not None and connection.is_connected():
            connection.close()
            logger.debug("共有データベース接続を閉じました")
    return results 
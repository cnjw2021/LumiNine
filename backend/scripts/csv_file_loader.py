import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import sys
import time
from core.db_config import get_db_connection_info, get_mysql_connection
from scripts.csv_data_loader import load_csv_to_table, load_multiple_csv_files

# スクリプトのディレクトリパスを基準にしたCSVファイルパスを取得する関数
BASE_CSV_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'csv')

def get_csv_path(filename):
    return os.path.join(BASE_CSV_DIR, filename)

def load_solar_terms_data(connection=None):
    """solar_terms CSVデータをロードする関数"""
    try:
        load_dotenv()
        print("solar_termsデータのロードを開始します...")
        row_count = load_csv_to_table(
            csv_filename='solar_terms_data.csv',
            table_name='solar_terms',
            truncate_table=True,
            use_load_data_infile=True,
            connection=connection
        )
        print(f"solar_termsのデータ挿入完了: {row_count}行")
        return row_count
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise

def load_solar_starts_data(connection=None):
    """solar_starts CSVデータをロードする関数"""
    try:
        load_dotenv()
        print("solar_startsデータのロードを開始します...")
        row_count = load_csv_to_table(
            csv_filename='solar_starts_data.csv',
            table_name='solar_starts',
            column_mapping=None,
            truncate_table=True,
            use_load_data_infile=True,
            connection=connection
        )
        print(f"solar_startsのデータ挿入完了: {row_count}行")
        return row_count
    except Exception as e:
        print(f"solar_startsデータロード中にエラーが発生しました: {e}")
        raise

def load_daily_astrology_data(connection=None):
    """daily_astrology CSVデータをロードする関数"""
    try:
        load_dotenv()
        print("daily_astrologyデータのロードを開始します...")
        row_count = load_csv_to_table(
            csv_filename='daily_astrology_data.csv',
            table_name='daily_astrology',
            truncate_table=True,
            use_load_data_infile=True,
            connection=connection
        )
        print(f"daily_astrologyのデータ挿入完了: {row_count}行")
        return row_count
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise

def load_main_star_acquired_fortune_message_data(connection=None):
    """acquired_fortune_message CSVデータをロードする関数"""
    try:
        load_dotenv()
        print("acquired_fortune_messageデータのロードを開始します...")
        row_count = load_csv_to_table(
            csv_filename='acquired_fortune_message_data.csv',
            table_name='acquired_fortune_message',
            truncate_table=True,
            use_load_data_infile=True,
            connection=connection
        )
        print(f"acquired_fortune_messageのデータ挿入完了: {row_count}行")
        return row_count
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise




def load_compatibility_readings_master_data(connection=None):
    """compatibility_readings_master CSVデータをロードする関数"""
    try:
        load_dotenv()
        print("compatibility_readings_masterデータのロードを開始します...")
        row_count = load_csv_to_table(
            csv_filename='compatibility_readings_master.csv',
            table_name='compatibility_readings_master',
            truncate_table=True,
            use_load_data_infile=True,
            connection=connection
        )
        print(f"compatibility_readings_masterのデータ挿入完了: {row_count}行")
        return row_count
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise

def load_compatibility_symbol_master_data(connection=None):
    """compatibility_symbol_master CSVデータをロードする関数"""
    try:
        load_dotenv()
        print("compatibility_symbol_masterデータのロードを開始します...")
        row_count = load_csv_to_table(
            csv_filename='compatibility_symbol_master.csv',
            table_name='compatibility_symbol_master',
            truncate_table=True,
            use_load_data_infile=True,
            connection=connection
        )
        print(f"compatibility_symbol_masterのデータ挿入完了: {row_count}行")
        return row_count
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise

def load_compatibility_symbol_pattern_master_data(connection=None):
    """compatibility_symbol_pattern_master CSVデータをロードする関数"""
    try:
        load_dotenv()
        print("compatibility_symbol_pattern_masterデータのロードを開始します...")
        row_count = load_csv_to_table(
            csv_filename='compatibility_symbol_pattern_master.csv',
            table_name='compatibility_symbol_pattern_master',
            truncate_table=True,
            use_load_data_infile=True,
            connection=connection
        )
        print(f"compatibility_symbol_pattern_masterのデータ挿入完了: {row_count}行")
        return row_count
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise

def load_star_life_guidance_data(connection=None):
    """star_life_guidance CSVデータをロードする関数"""
    try:
        load_dotenv()
        print("star_life_guidanceデータのロードを開始します...")
        row_count = load_csv_to_table(
            csv_filename='star_life_guidance.csv',
            table_name='star_life_guidance',
            truncate_table=True,
            use_load_data_infile=True,
            connection=connection
        )
        print(f"star_life_guidanceのデータ挿入完了: {row_count}行")
        return row_count
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise

def load_star_compatibility_matrix_data(connection=None):
    """star_compatibility_matrix CSVデータをロードする関数"""
    try:
        load_dotenv()
        print("star_compatibility_matrixデータのロードを開始します...")
        row_count = load_csv_to_table(
            csv_filename='star_compatibility_matrix.csv',
            table_name='star_compatibility_matrix',
            truncate_table=True,
            use_load_data_infile=True,
            connection=connection
        )
        print(f"star_compatibility_matrixのデータ挿入完了: {row_count}行")
        return row_count
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise

def load_user_account_data(connection=None):
    """user_account CSVデータをロードする関数"""
    try:
        load_dotenv()
        print("user_accountデータのロードを開始します...")
        row_count = load_csv_to_table(
            csv_filename='user_account.csv',
            table_name='users',
            truncate_table=False,
            use_load_data_infile=True,
            connection=connection
        )
        print(f"user_accountのデータ挿入完了: {row_count}行")
        return row_count
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise

def load_all_csv_data(target_tables=None):
    """すべてのCSVデータをロードする関数（target_tablesが指定された場合は、そのテーブルのみを対象とする）"""
    try:
        load_dotenv()
        print(f"CSVデータのロードを開始します... {'(Target: ' + ', '.join(target_tables) + ')' if target_tables else '(All)'}")
        # FILE権限付きコネクションを1回だけ生成
        connection = get_mysql_connection(require_file_privilege=True)
        try:
            # 基本的なCSVとテーブルのマッピング
            csv_table_mapping = {
                'zodiac_groups.csv': 'zodiac_groups',
                'zodiac_group_members.csv': 'zodiac_group_members',
                'hourly_star_zodiacs.csv': 'hourly_star_zodiacs',
                'solar_terms_data.csv': 'solar_terms',
                'solar_starts_data.csv': 'solar_starts',
                'daily_astrology_data.csv': 'daily_astrology',
                'main_star_acquired_fortune_message.csv': 'main_star_acquired_fortune_message',
                'compatibility_symbol_master.csv': 'compatibility_symbol_master',
                'compatibility_symbol_pattern_master.csv': 'compatibility_symbol_pattern_master',
                'compatibility_readings_master.csv': 'compatibility_readings_master',
                'star_life_guidance.csv': 'star_life_guidance',
                'star_compatibility_matrix.csv': 'star_compatibility_matrix',
                'pattern_switch_dates.csv': 'pattern_switch_dates',
            }
            
            # target_tables が指定されている場合はフィルタリング
            if target_tables:
                filtered_mapping = {}
                for csv_file, table_name in csv_table_mapping.items():
                    if table_name in target_tables:
                        filtered_mapping[csv_file] = table_name
                csv_table_mapping = filtered_mapping

            results = {}
            # 基本的なCSVファイルをロード
            if csv_table_mapping:
                results = load_multiple_csv_files(
                    connection,
                    csv_table_mapping,
                    truncate_tables=True,
                    use_load_data_infile=True
                )


            
            # user_accountデータを個別にロード（truncateしない）
            if not target_tables or 'users' in target_tables:
                user_connection = get_mysql_connection(require_file_privilege=True)
                try:
                    user_rows = load_user_account_data(user_connection)
                    results['users'] = user_rows
                finally:
                    if user_connection is not None and user_connection.is_connected():
                        user_connection.close()
            
            for table, count in results.items():
                print(f"{table}テーブルに{count}行のデータをロードしました")
            return results
        finally:
            if connection is not None and connection.is_connected():
                connection.close()
    except Exception as e:
        print(f"CSVデータロード中にエラーが発生しました: {e}")
        raise

if __name__ == "__main__":
    # ビルド中フラグを設定
    os.environ['BUILDING'] = 'true'
    
    # RECREATE_DB環境変数を確認
    recreate_db = os.environ.get('RECREATE_DB', 'false').lower() == 'true'
    
    if not recreate_db:
        print("RECREATE_DB環境変数がtrueではないため、CSVデータロードをスキップします")
        sys.exit(0)
    
    # すべてのCSVデータをロード
    try:
        load_all_csv_data()
    except Exception as e:
        print(f"予期せぬエラーが発生しましたが、ビルドを続行します: {e}")
        # ビルド時はエラーコード0で終了
        sys.exit(0) 
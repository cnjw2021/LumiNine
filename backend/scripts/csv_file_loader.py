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

def load_month_star_acquired_fortune_message_data(connection=None):
    """month_star_acquired_fortune_message CSVデータをロードする関数"""
    try:
        load_dotenv()
        print("month_star_acquired_fortune_messageデータのロードを開始します...")
        row_count = load_csv_to_table(
            csv_filename='month_star_acquired_fortune_message_data.csv',
            table_name='month_star_acquired_fortune_message',
            truncate_table=True,
            use_load_data_infile=True,
            connection=connection
        )
        print(f"month_star_acquired_fortune_messageのデータ挿入完了: {row_count}行")
        return row_count
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise

def load_compatibility_master_data(connection=None):
    """compatibility_master CSVデータをロードする関数"""
    try:
        load_dotenv()
        print("compatibility_masterデータのロードを開始します...")
        
        # 独自のコネクションが渡されていない場合は新しく作成
        should_close_connection = False
        if connection is None:
            connection = get_mysql_connection(require_file_privilege=True)
            should_close_connection = True
            
        try:
            # 9つのCSVファイルとそれに対応するテーブル名のマッピング
            csv_table_mapping = {
                'compatibility_master_1.csv': 'compatibility_master',
                'compatibility_master_2.csv': 'compatibility_master',
                'compatibility_master_3.csv': 'compatibility_master',
                'compatibility_master_4.csv': 'compatibility_master',
                'compatibility_master_5.csv': 'compatibility_master',
                'compatibility_master_6.csv': 'compatibility_master',
                'compatibility_master_7.csv': 'compatibility_master',
                'compatibility_master_8.csv': 'compatibility_master',
                'compatibility_master_9.csv': 'compatibility_master'
            }
            
            # 最初のファイルだけテーブルをtruncateする
            truncate_done = False
            total_rows = 0
            
            for csv_file, table_name in csv_table_mapping.items():
                # ファイルの存在確認
                csv_path = get_csv_path(csv_file)
                if not os.path.exists(csv_path):
                    print(f"ファイル {csv_file} が見つかりません。スキップします。")
                    continue
                
                try:
                    # 各ファイルをロード
                    row_count = load_csv_to_table(
                        connection=connection,
                        csv_filename=csv_file,
                        table_name=table_name,
                        truncate_table=not truncate_done,  # 最初のファイルのみtruncate
                        use_load_data_infile=True
                    )
                    
                    # 最初のファイルのロード後はtruncateしない
                    if not truncate_done:
                        truncate_done = True
                        
                    total_rows += row_count
                    print(f"ファイル {csv_file} から {row_count}行をロードしました")
                except Exception as e:
                    print(f"ファイル {csv_file} のロード中にエラーが発生しました: {e}")
                    # 一つのファイルのエラーで全体が失敗しないよう、続行する
            
            print(f"compatibility_masterのデータ挿入完了: 合計 {total_rows}行")
            return total_rows
        finally:
            if should_close_connection and connection is not None and connection.is_connected():
                connection.close()
                print("データベース接続を閉じました")
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

def load_all_csv_data():
    """すべてのCSVデータをロードする関数"""
    try:
        load_dotenv()
        print("すべてのCSVデータのロードを開始します...")
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
                'month_star_acquired_fortune_message.csv': 'month_star_acquired_fortune_message',
                'main_star_acquired_fortune_message.csv': 'main_star_acquired_fortune_message',
                'compatibility_symbol_master.csv': 'compatibility_symbol_master',
                'compatibility_symbol_pattern_master.csv': 'compatibility_symbol_pattern_master',
                'compatibility_readings_master.csv': 'compatibility_readings_master',
                'star_life_guidance.csv': 'star_life_guidance',
                'star_compatibility_matrix.csv': 'star_compatibility_matrix',
                'pattern_switch_dates.csv': 'pattern_switch_dates',
            }
            
            # 基本的なCSVファイルをロード
            results = load_multiple_csv_files(
                connection,
                csv_table_mapping,
                truncate_tables=True,
                use_load_data_infile=True
            )
            
            # compatibility_masterの9つのファイルを個別にロード
            # 新しいコネクションを作成（前のload_multiple_csv_filesでクローズされているため）
            compatibility_connection = get_mysql_connection(require_file_privilege=True)
            try:
                compatibility_rows = load_compatibility_master_data(compatibility_connection)
                results['compatibility_master'] = compatibility_rows
            finally:
                if compatibility_connection is not None and compatibility_connection.is_connected():
                    compatibility_connection.close()
            
            # user_accountデータを個別にロード（truncateしない）
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
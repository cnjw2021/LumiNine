import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
import sys
import time
from core.db_config import get_db_connection_info, get_postgres_connection
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
        # PostgreSQL接続を1回だけ生成
        connection = get_postgres_connection()
        try:
            # 基本的なCSVとテーブルのマッピング
            csv_table_mapping = {
                'zodiac_groups.csv': 'zodiac_groups',
                'zodiac_group_members.csv': 'zodiac_group_members',
                'hourly_star_zodiacs.csv': 'hourly_star_zodiacs',
                'solar_terms_data.csv': 'solar_terms',
                'solar_starts_data.csv': 'solar_starts',
                'daily_astrology_data.csv': 'daily_astrology',

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
                user_connection = get_postgres_connection()
                try:
                    user_rows = load_user_account_data(user_connection)
                    results['users'] = user_rows
                finally:
                    try:
                        user_connection.close()
                    except Exception:
                        pass
            
            for table, count in results.items():
                print(f"{table}テーブルに{count}行のデータをロードしました")
            return results
        finally:
            try:
                connection.close()
            except Exception:
                pass
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
import os
from datetime import timedelta
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

class Config:
    """アプリケーション設定"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # DATABASE_URLから接続情報を抽出する関数
    @staticmethod
    def parse_db_url():
        """DATABASE_URL環境変数からデータベース接続情報を抽出"""
        db_url = os.environ.get('DATABASE_URL')
        if db_url:
            try:
                # URLスキームの部分を一時的に置き換えてパース
                from urllib.parse import urlparse
                parsed = urlparse(db_url.replace('mysql+pymysql://', 'http://').replace('mysql+mysqldb://', 'http://'))
                return {
                    'user': parsed.username,
                    'password': parsed.password,
                    'host': parsed.hostname,
                    'port': parsed.port or '3306',
                    'name': parsed.path.strip('/').split('?')[0],
                    'charset': 'utf8mb4'
                }
            except Exception as e:
                print(f"DATABASE_URLの解析に失敗しました: {e}")
                return None
        return None
    
    # DATABASE_URLを優先し、個別の環境変数をフォールバックとして使用
    db_config = parse_db_url.__func__()
    
    # MySQL接続設定
    DB_USER = os.environ.get('DB_USER', db_config['user'] if db_config else 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', db_config['password'] if db_config else 'fortune_pass')
    DB_HOST = os.environ.get('DB_HOST', db_config['host'] if db_config else 'mysql')
    DB_PORT = os.environ.get('DB_PORT', db_config['port'] if db_config else '3306')
    DB_NAME = os.environ.get('DB_NAME', db_config['name'] if db_config else 'fortune_db')
    DB_CHARSET = os.environ.get('DB_CHARSET', db_config['charset'] if db_config else 'utf8mb4')
    
    # MySQL接続URL (mysqlclientを使用)
    if db_config:
        # DATABASE_URLが存在する場合はそれを使用
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    else:
        # 個別の環境変数から接続URLを構築
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset={DB_CHARSET}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # アカウント制限のデフォルト値（環境変数から初期値を取得）
    # この値は初期化時にのみ使用され、その後はテーブルから取得する
    ACCOUNT_LIMIT = int(os.environ.get('DEFAULT_ADMIN_ACCOUNT_LIMIT', 10))

    def get_account_limit(self):
        """アカウント制限数をデータベースから取得"""
        try:
            # 循環インポートを避けるため、ここでインポート
            from core.models import SystemConfig
            
            # データベースから設定値を取得
            limit = SystemConfig.get_by_key('ACCOUNT_LIMIT')
            if limit is not None:
                return int(limit)
            
            # データベースに設定がない場合はデフォルト値を返す
            return self.ACCOUNT_LIMIT
        except Exception:
            # エラーが発生した場合はデフォルト値を返す
            return self.ACCOUNT_LIMIT

# グローバル設定オブジェクト
_config = Config()

def get_config():
    """設定オブジェクトを取得する"""
    return _config 
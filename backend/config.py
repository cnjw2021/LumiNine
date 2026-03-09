import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """アプリケーション設定"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # DATABASE_URLから接続情報を抽出する関数
    @staticmethod
    def parse_db_url():
        """DATABASE_URL環境変数からデータベース接続情報を抽出 (PostgreSQL/MySQL 両対応)"""
        db_url = os.environ.get('DATABASE_URL')
        if db_url:
            try:
                from urllib.parse import urlparse
                # スキームを一時的に http:// に置き換えてパース
                normalized = db_url
                for scheme in ('postgresql+psycopg2://', 'postgresql://', 'postgres://',
                               'mysql+pymysql://', 'mysql+mysqldb://', 'mysql://'):
                    normalized = normalized.replace(scheme, 'http://')
                parsed = urlparse(normalized)
                return {
                    'user': parsed.username,
                    'password': parsed.password,
                    'host': parsed.hostname,
                    'port': parsed.port or 5432,
                    'name': parsed.path.strip('/').split('?')[0],
                }
            except Exception as e:
                print(f"DATABASE_URL解析失敗: {e}")
                return None
        return None

    db_config = parse_db_url.__func__()

    # 接続設定 (DATABASE_URL 優先、個別環境変数フォールバック)
    DB_USER = os.environ.get('DB_USER', db_config['user'] if db_config else 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', db_config['password'] if db_config else '')
    DB_HOST = os.environ.get('DB_HOST', db_config['host'] if db_config else 'postgres')
    DB_PORT = os.environ.get('DB_PORT', str(db_config['port']) if db_config else '5432')
    DB_NAME = os.environ.get('DB_NAME', db_config['name'] if db_config else 'luminine')

    # SQLAlchemy 接続 URI (PostgreSQL)
    if os.environ.get('DATABASE_URL'):
        # Supabase等の postgres:// スキームを psycopg2 対応形式に変換
        _raw_url = os.environ['DATABASE_URL']
        if _raw_url.startswith('postgres://'):
            _raw_url = 'postgresql+psycopg2://' + _raw_url[len('postgres://'):]
        elif _raw_url.startswith('postgresql://') and '+' not in _raw_url.split('://')[0]:
            _raw_url = 'postgresql+psycopg2://' + _raw_url[len('postgresql://'):]
        SQLALCHEMY_DATABASE_URI = _raw_url
    else:
        SQLALCHEMY_DATABASE_URI = (
            f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    ACCOUNT_LIMIT = int(os.environ.get('DEFAULT_ADMIN_ACCOUNT_LIMIT', 10))

    def get_account_limit(self):
        """アカウント制限数をデータベースから取得"""
        try:
            from core.models import SystemConfig
            limit = SystemConfig.get_by_key('ACCOUNT_LIMIT')
            if limit is not None:
                return int(limit)
            return self.ACCOUNT_LIMIT
        except Exception:
            return self.ACCOUNT_LIMIT

_config = Config()

def get_config():
    """設定オブジェクトを取得する"""
    return _config
import os
from dotenv import load_dotenv
from core.utils.logger import get_logger

# 環境変数の読み込み
load_dotenv()

# ロガーの初期化
logger = get_logger(__name__)

_db_conn_info_cache = None  # 追加: グローバルキャッシュ

def get_db_connection_info():
    """データベース接続情報を一元管理して返す（キャッシュ付き）"""
    global _db_conn_info_cache
    if _db_conn_info_cache is not None:
        return _db_conn_info_cache
    # DATABASE_URLが設定されている場合は、それを優先して解析
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        try:
            from urllib.parse import urlparse
            # SQLAlchemy形式のURLを標準形式に変換して解析
            normalized = db_url
            for prefix in ('postgresql+psycopg2://', 'postgresql+asyncpg://', 'mysql+pymysql://', 'mysql+mysqldb://'):
                if db_url.startswith(prefix):
                    scheme = prefix.split('+')[0]
                    normalized = scheme + '://' + db_url[len(prefix):]
                    break
            parsed = urlparse(normalized)
            
            host = parsed.hostname or os.environ.get('DB_HOST', 'postgres')
            user = parsed.username or os.environ.get('DB_USER', 'luminine')
            password = parsed.password or os.environ.get('DB_PASSWORD', 'luminine_password')
            port = str(parsed.port) if parsed.port else os.environ.get('DB_PORT', '5432')
            
            if parsed.path:
                database = parsed.path.strip('/').split('?')[0] or os.environ.get('DB_NAME', 'luminine')
            else:
                database = os.environ.get('DB_NAME', 'luminine')
                
            logger.debug(f"DATABASE_URLから接続情報を解析: host={host}, user={user}, database={database}")
        except Exception as e:
            logger.error(f"DATABASE_URLの解析に失敗しました: {e}")
            # 解析に失敗した場合は個別の環境変数を使用
            host = os.environ.get('DB_HOST', 'postgres')
            user = os.environ.get('DB_USER', 'luminine')
            password = os.environ.get('DB_PASSWORD', 'luminine_password')
            database = os.environ.get('DB_NAME', 'luminine')
            port = os.environ.get('DB_PORT', '5432')
    else:
        # 個別の環境変数から接続情報を取得（DB_*の命名規則を優先）
        host = os.environ.get('DB_HOST', 'postgres')
        user = os.environ.get('DB_USER', 'luminine') 
        password = os.environ.get('DB_PASSWORD', 'luminine_password')
        database = os.environ.get('DB_NAME', 'luminine')
        port = os.environ.get('DB_PORT', '5432')
    
    # 最終的な接続情報を返す
    _db_conn_info_cache = {
        'host': host,
        'user': user,
        'password': password,
        'database': database,
        'port': port,
    }
    return _db_conn_info_cache

def get_sqlalchemy_uri():
    """SQLAlchemy接続文字列を生成"""
    # DATABASE_URLが直接指定されている場合はそれを返す
    if 'DATABASE_URL' in os.environ:
        return os.environ.get('DATABASE_URL')
    
    # 接続情報から文字列を構築
    info = get_db_connection_info()
    return f"postgresql+psycopg2://{info['user']}:{info['password']}@{info['host']}:{info['port']}/{info['database']}"

def get_postgres_connection():
    """psycopg2接続を取得する"""
    import psycopg2
    
    connection_info = get_db_connection_info()
    
    try:
        connection = psycopg2.connect(
            host=connection_info['host'],
            user=connection_info['user'],
            password=connection_info['password'],
            dbname=connection_info['database'],
            port=connection_info['port'],
            connect_timeout=10
        )
        logger.debug(f"PostgreSQLに接続しました: {connection_info['host']} - {connection_info['user']} - {connection_info['database']}")
        return connection
    except Exception as e:
        logger.error(f"PostgreSQL接続エラー: {e}")
        raise
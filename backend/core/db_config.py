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
            parsed = urlparse(db_url.replace('mysql+pymysql://', 'http://').replace('mysql+mysqldb://', 'http://'))
            
            host = parsed.hostname or os.environ.get('DB_HOST', 'mysql')
            user = parsed.username or os.environ.get('DB_USER', 'ninestarki')
            password = parsed.password or os.environ.get('DB_PASSWORD', 'ninestarki_password')
            port = str(parsed.port) if parsed.port else os.environ.get('DB_PORT', '3306')
            
            if parsed.path:
                database = parsed.path.strip('/').split('?')[0] or os.environ.get('DB_NAME', 'ninestarki')
            else:
                database = os.environ.get('DB_NAME', 'ninestarki')
                
            logger.debug(f"DATABASE_URLから接続情報を解析: host={host}, user={user}, database={database}")
        except Exception as e:
            logger.error(f"DATABASE_URLの解析に失敗しました: {e}")
            # 解析に失敗した場合は個別の環境変数を使用
            host = os.environ.get('DB_HOST', 'mysql')
            user = os.environ.get('DB_USER', 'ninestarki')
            password = os.environ.get('DB_PASSWORD', 'ninestarki_password')
            database = os.environ.get('DB_NAME', 'ninestarki')
            port = os.environ.get('DB_PORT', '3306')
    else:
        # 個別の環境変数から接続情報を取得（DB_*の命名規則を優先）
        host = os.environ.get('DB_HOST', 'mysql')
        user = os.environ.get('DB_USER', 'ninestarki') 
        password = os.environ.get('DB_PASSWORD', 'ninestarki_password')
        database = os.environ.get('DB_NAME', 'ninestarki')
        port = os.environ.get('DB_PORT', '3306')
        
        # 注: 以下は後方互換性のための対応です。
        # 将来的には DB_* 形式の環境変数のみを使用するように統一することをお勧めします。
        # MySQLの環境変数が設定されている場合は、それも確認
        mysql_host = os.environ.get('MYSQL_HOST')
        mysql_user = os.environ.get('MYSQL_USER')
        mysql_password = os.environ.get('MYSQL_PASSWORD')
        mysql_database = os.environ.get('MYSQL_DATABASE')
        
        # MySQLの環境変数が設定されていれば、それを使用（DB_*が未設定の場合のフォールバック）
        if mysql_host and not os.environ.get('DB_HOST'):
            host = mysql_host
            logger.warning(f"非推奨: MYSQL_HOST環境変数が使用されました。DB_HOSTに移行してください: {host}")
        if mysql_user and not os.environ.get('DB_USER'):
            user = mysql_user
            logger.warning(f"非推奨: MYSQL_USER環境変数が使用されました。DB_USERに移行してください: {user}")
        if mysql_password and not os.environ.get('DB_PASSWORD'):
            password = mysql_password
            logger.warning("非推奨: MYSQL_PASSWORD環境変数が使用されました。DB_PASSWORDに移行してください")
        if mysql_database and not os.environ.get('DB_NAME'):
            database = mysql_database
            logger.warning(f"非推奨: MYSQL_DATABASE環境変数が使用されました。DB_NAMEに移行してください: {database}")
    
    # 最終的な接続情報を返す
    charset = os.environ.get('DB_CHARSET', 'utf8mb4')
    _db_conn_info_cache = {
        'host': host,
        'user': user,
        'password': password,
        'database': database,
        'port': port,
        'charset': charset
    }
    return _db_conn_info_cache

def get_sqlalchemy_uri():
    """SQLAlchemy接続文字列を生成"""
    # DATABASE_URLが直接指定されている場合はそれを返す
    if 'DATABASE_URL' in os.environ:
        return os.environ.get('DATABASE_URL')
    
    # 接続情報から文字列を構築
    info = get_db_connection_info()
    return f"mysql+pymysql://{info['user']}:{info['password']}@{info['host']}:{info['port']}/{info['database']}?charset={info['charset']}"

def get_mysql_connection(require_file_privilege=False):
    """mysql.connector接続を取得する"""
    import mysql.connector
    from mysql.connector import Error
    
    connection_info = get_db_connection_info()
    
    # FILE権限が必要な場合はrootユーザーを使用
    if require_file_privilege:
        # rootアカウントもしくは適切な権限を持つ他のユーザーを使用
        connection_info['user'] = os.environ.get('DB_ROOT_USER', os.environ.get('MYSQL_ROOT_USER', 'root'))
        connection_info['password'] = os.environ.get('DB_ROOT_PASSWORD', os.environ.get('MYSQL_ROOT_PASSWORD', 'rootpassword'))
        logger.debug(f"FILE権限のためrootユーザーを使用")
    
    try:
        connection = mysql.connector.connect(
            host=connection_info['host'],
            user=connection_info['user'],
            password=connection_info['password'],
            database=connection_info['database'],
            port=connection_info['port'],
            charset=connection_info['charset'],
            connect_timeout=10
        )
        logger.debug(f"MySQLに接続しました: {connection_info['host']} - {connection_info['user']} - {connection_info['database']}")
        return connection
    except Error as e:
        logger.error(f"MySQL接続エラー: {e}")
        raise 
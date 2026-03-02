import os
from datetime import timedelta
import logging

class BaseConfig:
    """基本設定"""
    DEBUG = False
    TESTING = False
    
    # データベース設定
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # 接続が切れた場合に自動的に再接続
        'pool_recycle': 3600,   # 1時間でコネクションをリサイクル
    }
    
    # CORS設定
    CORS_HEADERS = 'Content-Type'
    
    # JWT設定
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # データベース接続情報（デフォルト）
    DB_HOST = os.environ.get('DB_HOST', 'mysql')
    DB_USER = os.environ.get('DB_USER', 'ninestarki')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'ninestarki_password')
    DB_NAME = os.environ.get('DB_NAME', 'ninestarki')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_CHARSET = os.environ.get('DB_CHARSET', 'utf8mb4')
    DEFAULT_NOON_TIME = os.environ.get('DEFAULT_NOON_TIME', '12:00')  # 例: 12:00
    
    @classmethod
    def get_db_uri(cls):
        """データベース接続URIを生成"""
        if hasattr(cls, 'SQLALCHEMY_DATABASE_URI') and cls.SQLALCHEMY_DATABASE_URI:
            return cls.SQLALCHEMY_DATABASE_URI
        
        # DATABASE_URLが環境変数にある場合はそれを使用
        if 'DATABASE_URL' in os.environ:
            return os.environ.get('DATABASE_URL')
        
        # 接続情報から接続URIを生成
        return f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}?charset={cls.DB_CHARSET}"

class DevelopmentConfig(BaseConfig):
    """開発環境設定"""
    DEBUG = True
    
    # 開発環境のデフォルト値
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev_jwt_secret')
    SQLALCHEMY_DATABASE_URI = BaseConfig.get_db_uri()
    DEFAULT_ADMIN_ACCOUNT_LIMIT = int(os.environ.get('DEFAULT_ADMIN_ACCOUNT_LIMIT', '10'))

class ProductionConfig(BaseConfig):
    """本番環境設定"""
    
    @classmethod
    def validate_env_vars(cls):
        """本番環境で必要な環境変数をチェック"""
        required_vars = ['SECRET_KEY', 'JWT_SECRET_KEY']
        missing_vars = [var for var in required_vars if var not in os.environ]
        if missing_vars:
            raise ValueError(f"必須の環境変数が設定されていません: {', '.join(missing_vars)}")
    
    # 本番環境の設定（環境変数必須）
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = BaseConfig.get_db_uri()
    DEFAULT_ADMIN_ACCOUNT_LIMIT = int(os.environ.get('DEFAULT_ADMIN_ACCOUNT_LIMIT', '10'))

# 環境に応じた設定を選択
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """現在の環境に応じた設定を取得"""
    # ログ用
    logger = logging.getLogger(__name__)
    
    # FLASK_ENV、FLASK_DEBUG、FLASKENVの優先順位で環境を判断
    flask_env = os.environ.get('FLASK_ENV')
    flask_debug = os.environ.get('FLASK_DEBUG')
    flaskenv = os.environ.get('FLASKENV')
    
    # 環境変数の値をログに出力
    logger.info(f"FLASK_ENV: {flask_env}")
    logger.info(f"FLASK_DEBUG: {flask_debug}")
    logger.info(f"FLASKENV: {flaskenv}")
    
    # FLASK_DEBUGが0の場合は本番環境と判断
    if flask_debug == '0':
        is_production = True
        logger.info("FLASK_DEBUG=0のため本番環境として実行します")
    # FLASK_ENVがproductionの場合も本番環境
    elif flask_env and flask_env.lower() == 'production':
        is_production = True
        logger.info("FLASK_ENV=productionのため本番環境として実行します")
    # FLASKENVがproductionの場合も本番環境
    elif flaskenv and flaskenv.lower() == 'production':
        is_production = True
        logger.info("FLASKENV=productionのため本番環境として実行します")
    # どれも該当しない場合は開発環境と判断
    else:
        is_production = False
        logger.info("開発環境として実行します")
    
    # 環境に応じたConfigクラスを返す
    config_class = config['production'] if is_production else config['development']
    
    # 本番環境の場合のみ環境変数をチェック
    if is_production:
        try:
            config_class.validate_env_vars()
            logger.info("環境変数の検証に成功しました")
        except Exception as e:
            logger.error(f"環境変数の検証に失敗しました: {str(e)}")
    
    return config_class 
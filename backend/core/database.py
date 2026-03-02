from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import os
from dotenv import load_dotenv
from core.utils.logger import get_logger
from core.db_config import get_sqlalchemy_uri, get_db_connection_info

# 環境変数の読み込み
load_dotenv()

# ロガーの初期化
logger = get_logger(__name__)

db = SQLAlchemy()
Base = db.Model

# 読み取り専用・書き込み用のスコープ化ユーティリティ（シンプル版）
from contextlib import contextmanager


@contextmanager
def read_only_session():
    """読み取り専用のセッションスコープ。
    コミットは行わず、自動ロールバックする。
    """
    session = db.session
    try:
        yield session
    finally:
        session.close()


@contextmanager
def write_session():
    """書き込み用のセッションスコープ。
    成功時にコミット、例外時はロールバック。
    """
    session = db.session
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def init_db(app):
    """データベース接続の初期化を行う関数
    
    Note:
        テーブルの作成は mysql/init/ 配下の SQL ファイルで行われるため、
        ここでは SQLAlchemy の DB 接続初期化のみを行う
    """
    # 設定から接続情報を取得 (config.pyで環境変数から取得済み)
    # app.configにSQLALCHEMY_DATABASE_URIが既に設定されている場合はそれを使用
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        # 中央管理されたdb_configモジュールから接続情報を取得
        database_url = get_sqlalchemy_uri()
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    # 共通のSQLAlchemy設定
    if 'SQLALCHEMY_TRACK_MODIFICATIONS' not in app.config:
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    if 'SQLALCHEMY_ENGINE_OPTIONS' not in app.config:
        # データベース接続情報を取得
        db_config = get_db_connection_info()
        db_charset = db_config['charset']
                
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 3600,
            'connect_args': {
                'charset': db_charset
            }
        }
    
    logger.info(f"データベース接続を初期化: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    db.init_app(app) 
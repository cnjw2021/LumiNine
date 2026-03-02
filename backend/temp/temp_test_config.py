#!/usr/bin/env python
"""
設定モジュールのテスト
"""

import os
import sys
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 現在の環境変数を表示
logger.info("現在の環境変数:")
for key, value in os.environ.items():
    if key in ['FLASK_DEBUG', 'FLASK_ENV', 'FLASKENV', 'DATABASE_URL', 'DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']:
        logger.info(f"  {key}={value}")

try:
    # core.configをインポート
    logger.info("core.configモジュールをインポートします...")
    from core.config import get_config
    
    # 設定を取得
    logger.info("get_config()を呼び出します...")
    config = get_config()
    
    # 設定の内容を表示
    logger.info(f"設定クラス: {config.__name__}")
    logger.info(f"DB_HOST: {config.DB_HOST}")
    logger.info(f"DB_USER: {config.DB_USER}")
    logger.info(f"DB_NAME: {config.DB_NAME}")
    logger.info(f"SQLALCHEMY_DATABASE_URI: {config.SQLALCHEMY_DATABASE_URI}")
    
    logger.info("設定のテストが完了しました。")
    sys.exit(0)
except Exception as e:
    logger.error(f"エラーが発生しました: {str(e)}", exc_info=True)
    sys.exit(1) 
import logging
import os
from logging.handlers import TimedRotatingFileHandler
import pytz
from datetime import datetime
import sys

# プロジェクトのルートディレクトリを取得
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')

class JSTFormatter(logging.Formatter):
    """日本時間でログを出力するためのフォーマッター"""
    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        jst = pytz.timezone('Asia/Tokyo')
        return dt.astimezone(jst)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    # UTF-8エンコーディング処理は現代のPythonでは通常不要
    # def format(self, record):
    #     """ログメッセージをUTF-8でエンコードして出力"""
    #     if isinstance(record.msg, str):
    #         record.msg = record.msg.encode('utf-8', errors='replace').decode('utf-8')
    #     return super().format(record)

def _create_formatter():
    """共通のフォーマッターを作成する内部関数"""
    return JSTFormatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

def _ensure_log_directory():
    """ログディレクトリが存在することを確認する内部関数"""
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

def init_logger():
    """アプリケーション起動時に1回だけ呼び出されるロガー初期化関数"""
    # logsディレクトリがない場合は作成
    _ensure_log_directory()

    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 既存のハンドラーをクリア
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # アプリケーションロガーの設定
    logger = logging.getLogger('nines_star_ki')
    logger.setLevel(logging.INFO)

    # 既存のハンドラーをクリア
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # ファイルハンドラーの設定
    log_file = os.path.join(LOGS_DIR, 'app.log')
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='D',            # 日単位でローテーション
        interval=1,          # 1日ごと
        backupCount=30,      # 最大30個のバックアップファイルを保持
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)  # ファイルにもINFOログを出力

    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # 共通フォーマッターを使用
    formatter = _create_formatter()
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # ハンドラーを追加
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # デバッグログの出力テスト
    # logger.debug("ロガーが初期化されました")
    # logger.debug("ログレベル: %s", logging.getLevelName(logger.getEffectiveLevel()))

    return logger

def get_logger(name=None):
    """ロガーを取得する

    Args:
        name (str, optional): ロガー名。デフォルトはNone。

    Returns:
        logging.Logger: 設定済みのロガーインスタンス
    """
    # 環境変数からログレベルを取得（デフォルトはINFO）
    log_level_str = os.environ.get('LOG_LEVEL', 'INFO')
    
    # 文字列をloggingのレベル定数に変換
    log_level = getattr(logging, log_level_str.upper(), logging.DEBUG)
    
    # ロガーの取得
    if name:
        logger = logging.getLogger(name)
    else:
        logger = logging.getLogger('nines_star_ki')  # デフォルトのロガー名を設定

    # プロパゲーションを有効化（親ロガーにメッセージを伝播）
    logger.propagate = True

    # ログレベルの設定
    logger.setLevel(log_level)
    
    # 既存のハンドラーがなければ新しく追加
    if not logger.handlers:
        # ログディレクトリの確認
        _ensure_log_directory()
        
        # 共通フォーマッターを使用
        formatter = JSTFormatter(
            '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s'
        )
        
        # コンソールへの出力
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # ファイルへの出力
        file_handler = TimedRotatingFileHandler(
            os.path.join(LOGS_DIR, 'app.log'),
            when='D',            # 日単位でローテーション
            interval=1,          # 1日ごと
            backupCount=7,       # 最大7個のバックアップファイルを保持
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger 
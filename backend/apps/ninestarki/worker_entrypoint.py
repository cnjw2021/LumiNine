import os
import signal
from redis import Redis
from rq import Worker, Connection

# ワーカーが監視するキュー名
listen = ['pdf_queue']

def main():
    """RQワーカー用のエントリポイント。
    - Flaskアプリの初期化(create_app)をここで一度だけ行い、
      アプリケーションコンテキストをプッシュした状態でWorkerを起動する。
    - タスク関数側ではcreate_app()を呼ばず、現在のアプリコンテキストに依存する。
    """
    # app.pyのDIコンテナを用いたcreate_appでアプリを起動
    try:
        from backend.app import create_app
    except ImportError:
        from app import create_app
    flask_app = create_app()

    # Redis 接続設定
    redis_host = os.getenv('REDIS_HOST', 'redis')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    redis_conn = Redis(host=redis_host, port=redis_port)

    # アプリケーションコンテキストのもとでRQ Workerを起動
    with flask_app.app_context():
        with Connection(redis_conn):
            worker = Worker(map(str, listen))

            # SIGTERMを優雅に処理（Docker停止時）
            def handle_sigterm(signum, frame):
                try:
                    worker.log.info('SIGTERM received. Stopping worker...')
                finally:
                    raise SystemExit(0)
            signal.signal(signal.SIGTERM, handle_sigterm)

            worker.work()


if __name__ == '__main__':
    main()

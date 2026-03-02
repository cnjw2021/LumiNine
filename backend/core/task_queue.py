from redis import Redis
from rq import Queue
import os

_redis_host = os.getenv("REDIS_HOST", "redis")
_redis_port = int(os.getenv("REDIS_PORT", 6379))

# Redis との接続がアイドル状態で切断されてしまうのを防ぐため、
# `socket_keepalive=True` を設定し、`socket_timeout` を無制限にする。
# これによりコンテナ開発環境でも安定して接続を維持できる。
redis_conn = Redis(
    host=_redis_host,
    port=_redis_port,
    socket_keepalive=True,
    socket_timeout=None,
)

pdf_queue = Queue('pdf_queue', connection=redis_conn) 
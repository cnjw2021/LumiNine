# 非同期PDF生成機能 README

本ドキュメントでは、Redis + RQ を用いた **九星気学 PDF レポート** 非同期生成フローの仕組みと、開発環境のセットアップ手順を説明します。

---
## 1. 仕組み概要

```
┌────────┐  1.POST /api/pdf-jobs          ┌───────────┐
│FrontEnd│ ───────────────────────────▶ │ Flask API │
└────────┘                              └───────────┘
      ▲                                      │  enqueue()
      │ 3.GET status / download              ▼
┌────────┐  2.Redis enqueue           ┌────────────┐
│ Browser│ ◀──────────────────────────│ Redis      │
└────────┘                              └────────────┘
                                            │  pop()
                                            ▼
                                       ┌────────────┐
                                       │ RQ Worker  │ 4. PDF生成 → /tmp/pdf/{job_id}.pdf
                                       └────────────┘
```

1. フロントが **POST /api/pdf-jobs** を呼び出し、ジョブを登録。
2. Flask ルートは Redis キュー `pdf_queue` にジョブを投入し、`job_id` を返却（HTTP 202）。
3. フロントは **GET /api/pdf-jobs/{job_id}** をポーリングし、`status` を確認。
   * `finished` になったら `download_url` へアクセスして PDF を取得。
4. バックグラウンドの RQ ワーカーは Redis からジョブを取得し、
   `generate_ninestarki_pdf` を実行。完了後 `/tmp/pdf/{job_id}.pdf` に保存。

---
## 2. 主要コンポーネント

| ファイル / サービス                         | 役割 |
|---------------------------------------------|-----|
| `backend/core/task_queue.py`                | Redis 接続 & RQ キュー (`pdf_queue`) 定義 |
| `apps/ninestarki/routes/pdf_job_routes.py`  | 3 つの API エンドポイントを提供 |
| `generate_ninestarki_pdf` (サービス)        | `job_id` を受け取り PDF を `/tmp/pdf` へ保存 |
| **redis** コンテナ                           | メッセージブローカー & 結果ストア |
| **rq-worker** コンテナ                       | `rq worker pdf_queue` でジョブを処理 |

### エンドポイント一覧

| Method | Path                                   | 説明 |
|--------|----------------------------------------|------|
| POST   | `/api/pdf-jobs`                        | PDF 生成ジョブを登録。payload は既存同期 API と同内容。戻り値 `{ job_id }` |
| GET    | `/api/pdf-jobs/<job_id>`               | ジョブ状態を返す。`queued / started / finished / failed` |
| GET    | `/api/pdf-jobs/<job_id>/download`      | 完成 PDF をダウンロード |

---
## 3. Docker 開発環境

### 3.1 追加サービス

`docker-compose.dev.yml` に以下を追加済みです。

```yaml
dredis:
  image: redis:7-alpine
  volumes:
    - redis_data:/data   # 永続化
rq-worker:
  build:
    context: ./backend
    dockerfile: Dockerfile.dev
  command: rq worker pdf_queue --url redis://redis:6379
  depends_on:
    - redis
```

* **redis_data** ボリュームにより、コンテナ再作成後もキューデータが保持されます。

### 3.2 ビルド & 起動

```bash
docker compose -f docker-compose.dev.yml build --no-cache backend rq-worker
docker compose -f docker-compose.dev.yml up -d
```

確認:

```bash
docker exec redis redis-cli llen rq:queue:pdf_queue   # キュー長
```

---
## 4. フロントエンド実装例 (axios)

```ts
// 1. ジョブ登録
const res = await axios.post('/api/pdf-jobs', payload);
const jobId = res.data.job_id;

// 2. ポーリング関数
const waitForPdf = async (id: string) => {
  while (true) {
    const r = await axios.get(`/api/pdf-jobs/${id}`);
    if (r.data.status === 'finished') {
      window.location.href = r.data.download_url;  // 自動ダウンロード
      break;
    }
    if (r.data.status === 'failed') throw new Error('PDF生成失敗');
    await new Promise(res => setTimeout(res, 3000));
  }
};

waitForPdf(jobId);
```

---
## 5. よくある質問

### Q. Redis のデータはメモリだけでは？
A. `redis:7-alpine` は `/data` に AOF/RDB を保存します。`redis_data` ボリュームを Docker にマウントしているため、コンテナを削除してもデータは残ります。

### Q. 同時生成を増やしたい
A. `rq-worker` サービスの `scale` を増やす、または `docker compose up -d --scale rq-worker=3` のようにしてワーカー数を増やすだけで並列処理が可能です。

---
## 6. 運用メモ
* `/tmp/pdf` に出力されたファイルは定期バッチで削除してください（例: cron で 24h 後にクリア）。
* RQ Dashboard を導入すると Web UI でキューステータスを確認できます。
  ```bash
  pip install rq-dashboard
  rq-dashboard --redis-url redis://redis:6379
  ```

---
## 7. 開発 (`.dev`) と本番 compose の違い

|               | 開発 `docker-compose.dev.yml` | 本番 `docker-compose.yml` |
|---------------|--------------------------------|---------------------------|
| 使用 Dockerfile | `Dockerfile.dev` (ソースをボリュームマウント、ホットリロード向き) | `Dockerfile` (マルチステージビルドで軽量) |
| rq-worker コマンド | `rq worker pdf_queue --url redis://redis:6379` | 同左 |
| 目的 | macOS/WSL 等で長時間アイドル時に Redis との TCP 切断を防ぐ | Linux サーバ内で安定稼働する想定でデフォルト値利用 |

開発機でも本番同様の挙動にしたい場合は、prod 側のコマンドを dev に合わせる/またはその逆に統一してください。  
もし環境によって Redis との TCP セッションがアイドル切断される場合は、`backend/core/task_queue.py` 側で `socket_keepalive=True` や `socket_timeout=None` を設定するなど、Python クライアント側で制御してください。

以上。 

---
## 8. RQ ワーカーでの **Flask Application Context** について

PDF 生成サービス `generate_ninestarki_pdf` では、DB 参照（`StarAttribute.query …` など）を行うため **Flask のアプリケーションコンテキスト** が必須です。<br/>
RQ ワーカーは通常 Flask アプリを経由せずに関数を実行するため、そのままでは *"Working outside of application context"* エラーが発生します。

```text
RuntimeError: Working outside of application context.
```

### 対応方法

サービス関数の冒頭でアプリケーションコンテキストをプッシュし、終了時に必ず `ctx.pop()` で破棄します。

```python
from app import app as flask_app

# 関数先頭
ctx = flask_app.app_context()
ctx.push()

# … DB アクセスを含む処理 …

# 正常終了 or except/finally で必ず pop
ctx.pop()
```

本リポジトリでは `apps/ninestarki/services/pdf_generator.py` 内で上記を実装済みです。

> これにより、RQ ワーカー経由でも DB 参照付き PDF 生成が正常に完了し、`/api/pdf-jobs/{job_id}` が `finished` を返すようになります。

--- 
## 9. RQ ワーカーのビルド & 再起動手順

開発中に **`apps/ninestarki/services/*` や DB アクセス周り** を変更した場合、`rq-worker` イメージも再ビルドが必要です。

| サービス | コードがホットリロードされるか | 理由 |
|----------|------------------------------|------|
| **backend** | `./backend:/app` を volumes でマウントしているため、ファイル編集だけで即反映 | Flask dev サーバとして動作させるため |
| **rq-worker** | *マウント無し* (ビルド済みイメージを実行) | ワーカーは軽量実行が目的。コードを焼き込んだイメージなので変更時は再ビルドが必要 |

### 手順 (dev compose)

```bash
# 1. backend / rq-worker を同時にビルド
docker compose -f docker-compose.dev.yml build backend rq-worker

# 2. ワーカーのみ再起動 (依存サービスは止めない)
docker compose -f docker-compose.dev.yml up -d --no-deps rq-worker

# もしくは
docker compose -f docker-compose.dev.yml restart rq-worker
```

#### オプション解説
* `build backend rq-worker` : 指定サービスの Dockerfile を再実行して新しいイメージを作成。
* `--no-deps` : 依存サービス (redis など) を巻き込まずに対象コンテナだけを再作成／再起動する。

> これを忘れると、ワーカーだけ古いコードを実行し続け **`Working outside of application context`** などの予期せぬエラーが再発します。

---
## 10. ベストプラクティス: カスタムワーカースクリプト

本番・開発ともに **ワーカー専用ランチャースクリプト** を作成しておくと、
ログ設定や Flask Application Context の管理を 1 ヶ所に集約でき、保守性が高まります。

### 10.1 実装例 `apps/ninestarki/worker.py`

```python
from rq import Worker, Queue, Connection
from core.task_queue import redis_conn
from core.utils.logger import init_logger

# Flask アプリを読み込み
from app import app as flask_app  # or from backend.app import app as flask_app

init_logger()                      # ロガー初期化
ctx = flask_app.app_context(); ctx.push()  # Application Context

with Connection(redis_conn):
    Worker(["pdf_queue"]).work(with_scheduler=False)
```

### 10.2 compose の変更

```yaml
rq-worker:
  command: python -m apps.ninestarki.worker
```

これにより、

* **ログ**: `backend/logs/app.log` にワーカーのエラー/INFO も出力
* **DB & Flask 依存コード**: Application Context が常に有効で `RuntimeError` を回避

> 以降はサービス側で `init_logger()` や `app.app_context().push()` を都度呼ぶ必要がなくなります。

--- 
## 11. `/tmp/pdf` を共有するボリューム設定

`rq-worker` が生成した PDF を **backend** がダウンロード用に返すには、
両コンテナが同じファイルシステムを参照している必要があります。<br/>
そのため docker-compose で名前付きボリューム `pdf_tmp` を定義し、
サービスごとに `/tmp/pdf` へマウントしてください。

### 11.1 compose 例 (dev)

```yaml
volumes:
  pdf_tmp:
    driver: local

services:
  backend:
    volumes:
      - pdf_tmp:/tmp/pdf

  rq-worker:
    volumes:
      - pdf_tmp:/tmp/pdf
```

### 11.2 ポイント

* **書き込み側:** `generate_ninestarki_pdf()` が `/tmp/pdf/<job_id>.pdf` を作成。  
* **読み取り側:** backend の `/download` ルートが同じパスをチェック。  
* ボリューム未共有の場合 backend 側にファイルが無く 404 `{"error":"not ready"}` となる。

> ボリュームを追加した後は必ず `docker compose build` & `up -d` で反映してください。

--- 
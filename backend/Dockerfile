# ===================================================================
#  1. base - すべての環境の最小ステージ
# ===================================================================
FROM python:3.11-slim as base

# 環境変数を設定します。
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Asia/Tokyo
ENV LANG=en_US.UTF-8
ENV LC_CTYPE=en_US.UTF-8

# システムのタイムゾーンを設定します。
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# ロケールを生成します（UTF-8入力を有効化）
RUN apt-get update && apt-get install -y --no-install-recommends locales \
    && locale-gen en_US.UTF-8 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ===================================================================
#  2. builder - Python依存関係のインストール専用ステージ
# ===================================================================
FROM base as builder

# ビルドに必要なシステムパッケージをインストールします。
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=100 -r requirements.txt && \
    pip install gunicorn

# ===================================================================
#  3. development - 開発環境 ステージ
# ===================================================================
FROM base as development

# 開発環境で必要なすべてのシステムパッケージをインストールします (診断ツールを含む)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    fontconfig \
    default-mysql-client \
    # WeasyPrint 依存関係
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-xlib-2.0-0 shared-mime-info fonts-ipafont fonts-noto-cjk \
    # 開発の利便性のための診断ツール
    vim procps net-tools iputils-ping \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# non-root ユーザーを作成します。
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# builder ステージでインストールしたPythonパッケージをコピーします。
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

# non-root ユーザーによる作業ディレクトリの所有権を変更します。
RUN chown -R appuser:appgroup /app

USER appuser

# デフォルトの実行コマンド (docker-compose.ymlのcommandによって上書きされます)
CMD ["tail", "-f", "/dev/null"]

# ===================================================================
#  4. production - 最終運用環境 ステージ (デフォルト)
# ===================================================================
FROM base as production

# 運用環境で実行に必要な最小限のシステムパッケージをインストールします。
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    fontconfig \
    logrotate \
    cron \
    default-mysql-client \
    # WeasyPrint 依存関係
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-xlib-2.0-0 shared-mime-info fonts-ipafont fonts-noto-cjk \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# non-root ユーザーを作成します。
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# builder ステージでインストールしたPythonパッケージをコピーします。
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# アプリケーション コードと設定ファイルをコピーします。
COPY . .

# 現在のディレクトリ(/app)をPythonパッケージとしてインストールして、すべてのパス問題を解決します。
RUN pip install -e .

COPY logrotate.conf /etc/logrotate.d/gunicorn
RUN chmod 644 /etc/logrotate.d/gunicorn

# スクリプトに実行権限を付与し、すべての所有権を変更します。
RUN chmod +x /app/start.sh && \
    chmod +x /app/wait_for_db.py && \
    chown -R appuser:appgroup /app

# 運用時は cron/logrotate を起動するため root として開始し、
# アプリ本体(gunicorn)は start.sh 内で appuser に権限を降格して実行します。
USER root

CMD ["/app/start.sh"]

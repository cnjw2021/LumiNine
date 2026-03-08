# ===================================================================
#  1. base - すべての環境の最小ステージ
# ===================================================================
FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Asia/Tokyo
ENV LANG=en_US.UTF-8
ENV LC_CTYPE=en_US.UTF-8

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y --no-install-recommends locales \
    && locale-gen en_US.UTF-8 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ===================================================================
#  2. builder - Python依存関係のインストール専用ステージ
# ===================================================================
FROM base as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=100 -r requirements.txt && \
    pip install gunicorn

# ===================================================================
#  3. development - 開発環境ステージ
# ===================================================================
FROM base as development

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    vim procps net-tools iputils-ping \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app
RUN chown -R appuser:appgroup /app

USER appuser

CMD ["tail", "-f", "/dev/null"]

# ===================================================================
#  4. production - 最終運用環境ステージ (Cloud Run 最適化)
# ===================================================================
FROM base as production

# Cloud Run 最適化: WeasyPrint/logrotate/cron/mysql-client を除外
# 최소한의 런타임 패키지만 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

# パッケージとしてインストール
RUN pip install -e . --no-deps

RUN chmod +x /app/start.sh && \
    chown -R appuser:appgroup /app

# Cloud Run: 非rootユーザーで実行
USER appuser

# Cloud Run は $PORT を注入する。デフォルト 5001 は互換性確保のためのフォールバック
ENV PORT=5001

CMD ["/bin/sh", "/app/start.sh"]

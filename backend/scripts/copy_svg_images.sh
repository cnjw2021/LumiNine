#!/bin/bash

# SVG画像をフロントエンドからバックエンドにコピーするスクリプト

# スクリプトのパスを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# プロジェクトのルートディレクトリ
PROJECT_ROOT="$SCRIPT_DIR/../.."

# コピー元（フロントエンド）
SOURCE_DIR="$PROJECT_ROOT/frontend/public/images/main_star"

# コピー先（バックエンド）
TARGET_DIR="$PROJECT_ROOT/backend/apps/ninestarki/static/images/main_star"

# ターゲットディレクトリが存在するか確認し、なければ作成
mkdir -p "$TARGET_DIR"

# ファイルのコピー
echo "Copying SVG files from frontend to backend..."
cp "$SOURCE_DIR"/*.svg "$TARGET_DIR"/

# 確認のためにファイル一覧を表示
echo "Copied files:"
ls -la "$TARGET_DIR"

echo "SVG files copy completed." 
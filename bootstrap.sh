#!/bin/bash

# ==============================================================================
# ✨ サーバー 初期設定 スクリプト (Bootstrap)
# ==============================================================================
# このスクリプトは、新しいUbuntu/Debianサーバーで初回実行します。
# Docker、Docker Compose、Makeなど、プロジェクト実行に必要なすべてのシステムツールをインストールします。

# スクリプト実行中にエラーが発生した場合は、即座に終了します。
set -e

echo "### [1/3] システムパッケージリストを更新します... ###"
sudo apt-get update -y

echo "### [2/3] 必須パッケージ (make, git, curl など) をインストールします... ###"
sudo apt-get install -y build-essential git curl

echo "### [3/3] Docker と Docker Compose をインストールします... ###"
# Docker 公式インストールスクリプトを使用
if ! command -v docker &> /dev/null
then
    echo "Docker がインストールされていません。インストールを開始します。"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    # 現在のユーザーを docker グループに追加して、sudo なしで docker コマンドを使用できるようにします。
    sudo usermod -aG docker $USER
    echo "Docker インストール完了。sudo なしで docker を使用するには、ターミナルを再起動してください。"
else
    echo "Docker はすでにインストールされています。"
fi

echo ""
echo "✅ すべてのサーバー初期設定が完了しました。"
echo "これで、'make setup' コマンドでプロジェクトをデプロイできます。"
echo "Docker を新しくインストールした場合は、SSH 接続を切断して再接続してください。"
# macOS ローカル開発環境: Python インストール指針

このドキュメントは「`redis` など PyPI パッケージをホスト環境に入れようとしたら *SSL が無くて pip が失敗* する」「`brew install python@3.11` は破壊的か？」といった疑問に答えます。

---
## 1. 症状

```text
pip install redis
SSLError: HTTPSConnectionPool(host='pypi.org', ...): SSL module is not available
```

* macOS にプリインストールされている古い Python / 手動ビルドされた Python が **OpenSSL サポート無し** でコンパイルされている。
* そのため TLS が必須の PyPI から何も落とせない。

---
## 2. 最短の解決策

### (A) Homebrew 版 Python を使う

```bash
brew install python@3.11      # /opt/homebrew/bin/python3
python3 -m pip install --upgrade pip
```

* システムの `/usr/bin/python3` は上書きされず安全。
* PATH で Homebrew が先に来るとデフォルト `python3` が 3.11 に切替わる点だけ注意。

### (B) pyenv でビルドし直す

```bash
brew install openssl readline
CFLAGS="-I$(brew --prefix openssl)/include" \
LDFLAGS="-L$(brew --prefix openssl)/lib" \
pyenv install 3.10.14
pyenv global 3.10.14
```

---
## 3. 影響／副作用

| 項目 | Homebrew 3.11 を入れた場合 |
|------|----------------------------------|
| システム Python (/usr/bin) | 変更なし |
| ターミナル既定 `python3`, `pip3` | PATH の順序次第で 3.11 になる |
| 既存 venv | そのまま動作（中の Python は変更されない） |
| グローバル pip ツール | 再インストールが必要な場合あり |
| brew upgrade | 以後 3.11 系列がアップグレード対象になる |

> 既存プロジェクトが **特定バージョン前提** なら、pyenv でローカルバージョンを固定するのが安全です。

---
## 4. IDE だけ警告を消したい場合

Docker コンテナの Python を IDE Interpreter として設定できるなら、ホスト側 Python を触る必要はありません。
警告が邪魔なだけならソースに `# type: ignore` を追加する手もあります。

例:
```python
from redis import Redis  # type: ignore
```

---
## 5. まとめ

1. **本格的にパッケージを入れたい** → Homebrew 版 or pyenv ビルドの SSL 対応 Python を用意。
2. **Docker でしか実行しない** → IDE をコンテナ Python に切替 or `# type: ignore` で静的解析だけ黙らせる。

どちらを選ぶかはプロジェクト運用ポリシーに合わせてください。 
# テストディレクトリ

このディレクトリには、九星気学アプリケーションのテストコードが含まれています。

## テストファイル

- `test_db.py` - データベース接続とテーブル構造のテスト
- `test_calendar_utils.py` - カレンダーユーティリティ関数のテスト
- `test_eto_comparison.py` - 干支計算方法の比較テスト
- `test_korean_eto.py` - 韓国式干支計算アルゴリズムのテスト
- `test_stellar_phases.py` - 夏至・冬至および陽遁・陰遁の計算テスト（旧名：test_solstice_yinyang.py）

## 実行方法

各テストファイルは、以下のコマンドで実行できます：

```bash
# ローカル環境での実行
python backend/tests/test_db.py
python backend/tests/test_calendar_utils.py
python backend/tests/test_eto_comparison.py
python backend/tests/test_korean_eto.py
python backend/tests/test_stellar_phases.py

# Dockerコンテナ内での実行（推奨）
docker exec backend-container python tests/test_db.py
docker exec backend-container python tests/test_calendar_utils.py
docker exec backend-container python tests/test_eto_comparison.py
docker exec backend-container python tests/test_korean_eto.py
docker exec backend-container python tests/test_stellar_phases.py
```

### test_stellar_phases.py のコマンドラインオプション

`test_stellar_phases.py`は以下のコマンドラインオプションをサポートしています：

```bash
# 特定の年のみを計算する場合
python backend/tests/test_stellar_phases.py -y 2024
# または
python backend/tests/test_stellar_phases.py --year 2024

# 指定範囲の年を計算する場合
python backend/tests/test_stellar_phases.py -r 1930 2050
# または
python backend/tests/test_stellar_phases.py --range 1930 2050

# ヘルプを表示
python backend/tests/test_stellar_phases.py -h
```

引数を指定しない場合、デフォルトで1900年から2052年までの範囲が計算されます。

## データベース初期化用情報の生成

`test_stellar_phases.py`の出力は、`stellar_cycles`テーブルの初期データとして使用できます。以下のように実行して出力をリダイレクトすることで、INSERT文の基礎データを作成できます：

```bash
docker exec backend-container python tests/test_stellar_phases.py > stellar_cycles_data.txt
```

出力されたデータは、日付のみで時刻情報がないため、必要に応じて「00:00:00」などのデフォルト時刻を追加してSQL INSERT文に変換します。

## 注意事項

- テストを実行する前に、Dockerコンテナが起動していることを確認してください。
- 天体計算テスト（test_stellar_phases.py）は初回実行時にエフェメリスデータをダウンロードするため、インターネット接続が必要です。
- エフェメリスデータ（de421.bsp）は1899年7月29日から2053年10月9日までの期間のみをカバーしているため、この範囲外の日付は計算できません。
- 干支計算テストは既知の日付と比較し、九星気学の計算が正確であることを検証します。- SSL証明書検証エラーが発生した場合、テストスクリプトは自動的に証明書検証をバイパスします（開発環境専用）。 

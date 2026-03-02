# 九星気学相性鑑定システムのデータモデル

## 概要

九星気学の相性鑑定システムは、複雑な相性パターンを分解し、柔軟で効率的な鑑定を実現するためのデータモデルです。以下の主要コンポーネントから構成されています。

## 主要テーブル構成

### 1. 相性基本要素 (`symbol_elements`)
個々の相性記号（★、○、P、F、N、▲、◆など）とその意味を定義します。

| フィールド | 説明 |
|------------|------|
| id | 主キー |
| symbol | 相性記号（★、○、P、F、N、▲、◆など） |
| meaning | 記号の意味（最高、良好、ビジネスなど） |
| description | 詳細説明 |
| weight | 重み付け（表示順や重要度） |
| is_positive | 肯定的か否定的か |

### 2. 相性パターン (`compatibility_patterns`)
複合的な相性パターン（★P▲、○○▲など）の定義です。

| フィールド | 説明 |
|------------|------|
| code | パターンコード（主キー） |
| symbol | 相性記号の組み合わせ |
| symbol_meaning | 記号の意味 |
| name | パターン名称 |
| description | パターンの説明 |

### 3. パターン要素関連 (`pattern_elements`)
複合パターンを基本要素に分解して関連付けます。

| フィールド | 説明 |
|------------|------|
| id | 主キー |
| pattern_code | パターンコード（外部キー） |
| symbol | 基本要素の記号（外部キー） |
| position | 表示位置 |

### 4. 相性データ (`compatibility_data`)
本命星と生まれ月の組み合わせによる相性情報を格納します。

| フィールド | 説明 |
|------------|------|
| id | 主キー |
| main_star | 主星番号 |
| main_birth_month | 主星の生まれ月 |
| target_star | 対象星番号 |
| target_birth_month | 対象星の生まれ月 |
| symbols_male | 男性の相性記号 |
| symbols_female | 女性の相性記号 |
| pattern_code | パターンコード（外部キー、NULL許容） |

### 5. 相性鑑定文 (`compatibility_readings`)
相性パターンに対応する鑑定文を格納します。

| フィールド | 説明 |
|------------|------|
| id | 主キー |
| pattern_code | パターンコード（外部キー） |
| gender | 性別（男性/女性/NULL） |
| reading_type | 鑑定文タイプ |
| title | 鑑定タイトル |
| content | 鑑定内容 |

### 6. 基本要素の鑑定文 (`symbol_element_readings`)
基本要素ごとの鑑定文を格納します。

| フィールド | 説明 |
|------------|------|
| id | 主キー |
| symbol | 相性記号（外部キー） |
| gender | 性別（男性/女性/NULL） |
| reading_type | 鑑定文タイプ |
| title | 鑑定タイトル |
| content | 鑑定内容 |

## データの流れと鑑定プロセス

1. ユーザーの本命星・生まれ月と相手の本命星・生まれ月を入力
2. `compatibility_data`テーブルから該当する相性シンボル（例：「◎◎▲」）とパターンコードを取得
3. パターンコードが存在する場合:
   - `compatibility_readings`テーブルから対応する鑑定文を表示
4. パターンコードが存在しない場合または詳細が必要な場合:
   - `pattern_elements`テーブルを使って相性シンボルを基本要素に分解
   - 各基本要素に対応する鑑定文を`symbol_element_readings`テーブルから取得して組み合わせる

## 利点

- **効率性**: 147種類の複合パターンすべてに個別の鑑定文を用意する必要がなくなります
- **柔軟性**: 新しいパターンが追加された場合でも、基本要素の組み合わせとして表現できます
- **一貫性**: 基本要素の鑑定文が一貫しているため、複合パターンの鑑定も一貫性が保たれます
- **データ量削減**: パターンコードがNULL許容のため、既存の大量データ（compatibility_7.csvなど）もそのまま利用できます

## 実装例

```sql
-- 特定の相性パターンに対応する鑑定文を取得する
SELECT cr.title, cr.content
FROM compatibility_data cd
JOIN compatibility_readings cr ON cd.pattern_code = cr.pattern_code
WHERE cd.main_star = 2 AND cd.main_birth_month = 1 
AND cd.target_star = 3 AND cd.target_birth_month IS NULL
AND cr.gender = 'male' AND cr.reading_type = 'detailed';

-- パターンコードがない場合、シンボルを分解して基本要素の鑑定文を取得する
SELECT se.symbol, ser.title, ser.content
FROM compatibility_data cd
JOIN pattern_elements pe ON cd.symbols_male = pe.pattern_code
JOIN symbol_elements se ON pe.symbol = se.symbol
JOIN symbol_element_readings ser ON se.symbol = ser.symbol
WHERE cd.main_star = 7 AND cd.main_birth_month = 5
AND cd.target_star = 9 AND cd.target_birth_month = 8
AND ser.gender = 'male' AND ser.reading_type = 'summary'
ORDER BY pe.position;
``` 
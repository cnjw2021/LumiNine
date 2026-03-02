# 九星盤マーカー表示共通化メモ

作成日: 2025-07-05

## 背景
WeasyPrint で出力する PDF 内に 3 つのセクション（direction_fortune, monthly_fortune, yearly_fortune）が存在し、それぞれで九星盤に対して吉凶マーカーを配置している。

* direction_fortune.html → テーブル 2 枚重ね(0°+45°) 方式で **正確**
* monthly_fortune.html / yearly_fortune.html → CSS で％座標指定しているが **誤差** が出ている

メンテナンス性向上と位置ズレ解消のため、Direction Fortune のロジックを基準に 3 ファイルを共通マクロ化する。

---
## 方針
1. **共通パーシャル** `templates/ninestarkey_report/partials/marker_macros.html`
   * 方位→座標を 2×2 テーブル + 45°回転テーブルの組合せで算出
   * `macro chart(bg_url, directions_dict, main_star_number)` で呼び出し
2. **partial の座標マッピング** は `marker_map.html` 内に固定値で保持（調整はここだけ）
3. 既存 CSS は最小限流用。
   * `.direction-badge`, `.badge-lucky`, `.badge-unlucky` は共通で使用
4. 3 セクションはマクロ呼び出しに置換。
   * 旧 CSS の `.marker-*` 座標指定は削除 or 無効化（不要）
5. WeasyPrint で一括確認 → 誤差があれば `marker_map` の % を調整すれば全セクション反映。

---
## 実装ステップ
1. `partials/marker_map.html` と `marker_macros.html` を追加
2. `direction_fortune.html` の九星盤部分をマクロに置換（テスト基準）
3. monthly / yearly も同様に置換
4. CSS クリーンアップ

---
## 注意点 (WeasyPrint)
* テーブル・絶対配置はいずれも OK。`transform: rotate()` も PDF 化可能
* `position:absolute` 要素同士が重なっても z-index 反映される
* `%` ベースで指定すると 200×200 コンテナでも崩れにくい
* 画像(SVG) は `img` タグ／`background-image` どちらでも可

--- 
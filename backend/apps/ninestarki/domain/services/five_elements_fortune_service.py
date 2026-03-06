"""五行相生に基づく方位吉方判定ドメインサービス.

設計原則 (OCP / Clean Architecture):
- StarGridPattern.get_fortune_status() が出力した凶殺判定結果に対し、
  五行相生の関係で fortune_level (最大吉方/吉方/中立) を上書きする。
- 追加ルール (定位対冲、天道、小児殺 等) は同じインターフェースで
  新しいサービスとして追加でき、既存コードを修正する必要がない (OCP)。

使用法 (UseCase 層) :
    svc = FiveElementsFortuneService()
    directions = grid_pattern.get_fortune_status(params)
    svc.enrich(directions, main_star=7, grid_pattern=grid)
"""
from __future__ import annotations

from typing import Any, Dict


# ── 定数 ──────────────────────────────────────────────

# 九星 → 五行マッピング
STAR_ELEMENTS: Dict[int, str] = {
    1: "water",   # 一白水星
    2: "earth",   # 二黒土星
    3: "wood",    # 三碧木星
    4: "wood",    # 四緑木星
    5: "earth",   # 五黄土星
    6: "metal",   # 六白金星
    7: "metal",   # 七赤金星
    8: "earth",   # 八白土星
    9: "fire",    # 九紫火星
}

# 相生関係: 元素 X → 元素 Y を生む
ELEMENT_GENERATES: Dict[str, str] = {
    "wood": "fire",    # 木生火
    "fire": "earth",   # 火生土
    "earth": "metal",  # 土生金
    "metal": "water",  # 金生水
    "water": "wood",   # 水生木
}


# ── Service ───────────────────────────────────────────

class FiveElementsFortuneService:
    """五行相生で方位の fortune_level を判定する Domain Service.

    - best_auspicious (最大吉方): 方位星の五行が本命星の五行を **生む**
      例) 土→金: 二黒(土) が七赤(金) を生む
    - auspicious (吉方): 本命星の五行が方位星の五行を生む / 同じ五行 (比和)
      例) 金→水: 七赤(金) が一白(水) を生む
    - neutral (中立): 相克 等、相生でない関係
    - inauspicious (凶): 5凶殺に該当 (StarGridPattern 側で判定済み)
    """

    def enrich(
        self,
        directions: Dict[str, Dict[str, Any]],
        *,
        main_star: int,
        grid_pattern: Any,
    ) -> None:
        """directions dict を **in-place** で更新する.

        Args:
            directions: get_fortune_status() の戻り値 (方位 → 結果 dict)
            main_star: 本命星 (1–9)
            grid_pattern: StarGridPattern インスタンス (方位別の星番号取得用)
        """
        main_element = STAR_ELEMENTS.get(main_star, "")
        if not main_element:
            return

        # grid_pattern から方位→星番号マップを作成 (属性がない場合は安全にスキップ)
        _DIR_ATTRS = [
            "north", "northeast", "east", "southeast",
            "south", "southwest", "west", "northwest",
        ]
        star_map: Dict[str, int] = {}
        for attr in _DIR_ATTRS:
            val = getattr(grid_pattern, attr, None)
            if val is not None:
                star_map[attr] = val

        if not star_map:
            return

        for direction, result in directions.items():
            # 凶殺判定済みの方位はスキップ
            if result.get("fortune_level") == "inauspicious":
                continue

            star_number = star_map.get(direction)
            if star_number is None:
                continue

            star_element = STAR_ELEMENTS.get(star_number, "")

            # 最大吉方: 方位星 → 本命星 を生む
            if ELEMENT_GENERATES.get(star_element) == main_element:
                result["fortune_level"] = "best_auspicious"
                result["is_auspicious"] = True

            # 吉方: 本命星 → 方位星 を生む
            elif ELEMENT_GENERATES.get(main_element) == star_element:
                result["fortune_level"] = "auspicious"
                result["is_auspicious"] = True

            # 比和: 同じ五行
            elif star_element == main_element:
                result["fortune_level"] = "auspicious"
                result["is_auspicious"] = True

            else:
                # 相克等 → 中立
                result["fortune_level"] = "neutral"
                result["is_auspicious"] = None

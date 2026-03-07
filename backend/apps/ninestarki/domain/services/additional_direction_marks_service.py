"""追加方位マーク判定ドメインサービス (定位対冲・小児殺・天道).

設計原則 (OCP / Clean Architecture):
- FiveElementsFortuneService で判定済みの fortune_level に対し、
  追加ルールで **ダウングレード** する。既存サービスの修正は不要。
- 各ルールはデータ駆動 (ルックアップテーブル) で実装し、
  新しいルール追加時にもこのファイル内の追記のみで完結する。

ルール:
  1. 定位対冲: 星が「定位」の反対に配置 → auspicious/best_auspicious → neutral
  2. 小児殺: 月支で決まる凶方位 → auspicious/best_auspicious → neutral
  3. 天道: 月支で決まる特殊吉方 → 参考情報のみ (fortune_level 変更なし)

使用法 (UseCase 層):
    svc = AdditionalDirectionMarksService()
    svc.enrich(directions, grid_pattern=grid, month_branch="卯")
"""
from __future__ import annotations

from typing import Any, Dict


# ── 定位対冲 ─────────────────────────────────────────

# 各星の定位（ホーム方位）
STAR_HOME_DIRECTION: Dict[int, str] = {
    1: "north",       # 一白水星 → 坎(北)
    2: "southwest",   # 二黒土星 → 坤(南西)
    3: "east",        # 三碧木星 → 震(東)
    4: "southeast",   # 四緑木星 → 巽(東南)
    # 5 は中宮固定 → 定位対冲なし
    6: "northwest",   # 六白金星 → 乾(西北)
    7: "west",        # 七赤金星 → 兌(西)
    8: "northeast",   # 八白土星 → 艮(東北)
    9: "south",       # 九紫火星 → 離(南)
}

# 方位の反対関係
OPPOSITE_DIRECTIONS: Dict[str, str] = {
    "north": "south", "south": "north",
    "northeast": "southwest", "southwest": "northeast",
    "east": "west", "west": "east",
    "southeast": "northwest", "northwest": "southeast",
}


# ── 小児殺 ──────────────────────────────────────────

# 月支 → 小児殺の方位
# 典型的な周期: S→NW→W→SE→N→SW→E→NE を 12 支に割り当て
SHOUNI_SATSU: Dict[str, str] = {
    "寅": "south",
    "卯": "northwest",    # 参照サービスで確認済み (2026年3月)
    "辰": "west",
    "巳": "southeast",
    "午": "north",
    "未": "southwest",
    "申": "east",
    "酉": "northeast",
    "戌": "south",
    "亥": "northwest",
    "子": "west",
    "丑": "southeast",
}


# ── 天道 ──────────────────────────────────────────

# 月支 → 天道の方位 (参考情報のみ; fortune_level 変更なし)
TENDO_DIRECTION: Dict[str, str] = {
    "寅": "northwest",
    "卯": "southwest",    # 参照サービスで確認済み (2026年3月)
    "辰": "north",
    "巳": "southwest",
    "午": "northwest",
    "未": "north",
    "申": "southwest",
    "酉": "northwest",
    "戌": "north",
    "亥": "southwest",
    "子": "northwest",
    "丑": "north",
}


# ── Service ───────────────────────────────────────────

class AdditionalDirectionMarksService:
    """追加方位マーク (定位対冲・小児殺・天道) を判定する Domain Service.

    FiveElementsFortuneService の **後** に適用し、
    吉方判定済みの方位をダウングレードする。
    """

    @staticmethod
    def _append_reason(
        result: Dict[str, Any], label: str,
    ) -> None:
        """Append *label* to the ``reason`` field of *result* (comma-separated, dedup)."""
        reason = result.get("reason")
        if not reason:
            result["reason"] = label
        elif label not in reason:
            result["reason"] = reason + ", " + label

    def enrich(
        self,
        directions: Dict[str, Dict[str, Any]],
        *,
        grid_pattern: Any,
        month_branch: str,
    ) -> None:
        """directions dict を **in-place** で更新.

        Args:
            directions: fortune_level 判定済みの方位 dict
            grid_pattern: StarGridPattern (方位別の星番号取得用)
            month_branch: 月支 (例: "卯")
        """
        # grid_pattern → 方位: 星番号マップ
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

        # ── 1) 定位対冲 ──
        for direction, star_number in star_map.items():
            home = STAR_HOME_DIRECTION.get(star_number)
            if home is None:
                continue
            opposite = OPPOSITE_DIRECTIONS.get(home)
            if direction == opposite:
                result = directions.get(direction)
                if result and result.get("fortune_level") in (
                    "best_auspicious", "auspicious",
                ):
                    result["fortune_level"] = "neutral"
                    result["is_auspicious"] = None
                if result:
                    result.setdefault("additional_marks", []).append("teii_taichuu")
                    self._append_reason(result, "定位対冲")

        # ── 2) 小児殺 ──
        shouni_dir = SHOUNI_SATSU.get(month_branch)
        if shouni_dir and shouni_dir in directions:
            result = directions[shouni_dir]
            if result.get("fortune_level") in ("best_auspicious", "auspicious"):
                result["fortune_level"] = "neutral"
                result["is_auspicious"] = None
            result.setdefault("additional_marks", []).append("shouni_satsu")
            self._append_reason(result, "小児殺")

        # ── 3) 天道 (参考情報のみ) ──
        tendo_dir = TENDO_DIRECTION.get(month_branch)
        if tendo_dir and tendo_dir in directions:
            directions[tendo_dir].setdefault(
                "additional_marks", [],
            ).append("tendo")
            self._append_reason(directions[tendo_dir], "天道")

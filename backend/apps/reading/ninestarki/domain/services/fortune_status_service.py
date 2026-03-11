"""方位吉凶判定ドメインサービス.

StarGridPattern モデルから抽出した純粋な吉凶判定ロジック。
ORM 依存なし — grid_pattern オブジェクトの属性（north, south, ...）のみ参照。

Issue #128: モデル責務分解 (定数/検証/計算 → Domain Service へ)
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from apps.reading.ninestarki.domain.constants.direction_constants import (
    OPPOSITE_POSITIONS,
)
from core.utils.calendar_utils import get_opposite_zodiac_direction
from core.utils.logger import get_logger

logger = get_logger(__name__)


class FortuneStatusService:
    """九星盤の方位吉凶を判定する Domain Service (stateless)."""

    # ──────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────

    def get_fortune_status(
        self, grid_pattern: Any, params: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """各方位の吉凶状態を判定して返す.

        Args:
            grid_pattern: StarGridPattern インスタンス (方位別の星番号を属性で保持)
            params: 吉凶判定に必要なパラメータ
                - main_star (int): 本命星の番号（1-9）
                - month_star (int): 月命星の番号（1-9）
                - zodiac (str): 今年の干支（例: "甲寅"）

        Returns:
            Dict[str, Dict[str, Any]]: 各方位の吉凶状態と具体的なマーク

        Raises:
            ValueError: パラメータが不正な場合
            RuntimeError: 判定処理中に想定外のエラーが発生した場合
        """
        # パラメータの取得と検証
        main_star = params.get('main_star', 0)
        month_star = params.get('month_star', 0)
        zodiac = params.get('zodiac', '')

        if not all([isinstance(main_star, int), isinstance(month_star, int), isinstance(zodiac, str)]):
            raise ValueError("Invalid parameter types")

        if not (1 <= main_star <= 9 and 1 <= month_star <= 9):
            raise ValueError("Star numbers must be between 1 and 9")

        # 干支の向かい側の方位を取得（破）
        opposite_zodiac_direction = ""
        try:
            opposite_zodiac_direction = get_opposite_zodiac_direction(zodiac)
        except ValueError as e:
            logger.error(f"Error determining opposite direction from zodiac: {str(e)}")
            logger.warning("Continuing without opposite zodiac direction")

        # 暗剣殺の星を取得
        dark_sword_star = self.get_dark_sword_star(grid_pattern)

        # 各方位の星番号を取得
        directions = self._build_direction_map(grid_pattern)

        # 本命星と月命星の位置を追跡（1つだけ）
        main_star_position = None
        month_star_position = None

        # 各方位の吉凶を判定
        results: Dict[str, Dict[str, Any]] = {}

        # 最初のパス: 基本的な凶殺判定を行う（五黄殺・暗剣殺・本命殺・月命殺・水火殺・破 など）
        for direction, star_number in directions.items():
            result: Dict[str, Any] = {
                "is_auspicious": True,
                "reason": None,
                "marks": [],
                "fortune_level": None,  # domain service が五行判定で上書きする
            }

            if star_number == 5:
                result["is_auspicious"] = False
                result["reason"] = "五黄殺"
                result["marks"].append("five_yellow")

            # ２）暗剣殺の判定
            if dark_sword_star == -1:
                result["marks"].append("no_dark_sword_center_five")
            else:
                if star_number == dark_sword_star:
                    result["is_auspicious"] = False
                    result["reason"] = "暗剣殺"
                    result["marks"].append("dark_sword")

            # ３）本命星と月命星の判定
            if star_number == main_star:
                result["is_auspicious"] = False
                result["reason"] = "本命殺" if not result["reason"] else result["reason"] + ", 本命殺"
                result["marks"].append("main_star")
                main_star_position = direction

            if star_number == month_star:
                result["is_auspicious"] = False
                result["reason"] = "月命殺" if not result["reason"] else result["reason"] + ", 月命殺"
                result["marks"].append("month_star")
                month_star_position = direction

            # ４）水火殺の判定
            if (star_number == 1 or star_number == 9) and (grid_pattern.south == 1 or grid_pattern.north == 9):
                result["is_auspicious"] = False
                result["reason"] = "水火殺" if not result["reason"] else result["reason"] + ", 水火殺"
                result["marks"].append("water_fire")

            # 5）干支の向かい側（破）の判定
            if direction == opposite_zodiac_direction and opposite_zodiac_direction:
                result["is_auspicious"] = False
                result["reason"] = "破" if not result["reason"] else result["reason"] + ", 破"
                result["marks"].append("opposite_zodiac")

            results[direction] = result

        # 本命的殺
        if main_star_position:
            opposite_pos = OPPOSITE_POSITIONS.get(main_star_position)
            if opposite_pos:
                results[opposite_pos]["is_auspicious"] = False
                results[opposite_pos]["reason"] = "本命的殺" if not results[opposite_pos]["reason"] else results[opposite_pos]["reason"] + ", 本命的殺"
                results[opposite_pos]["marks"].append("main_star_opposite")

        # 月命的殺
        if month_star_position:
            opposite_pos = OPPOSITE_POSITIONS.get(month_star_position)
            if opposite_pos:
                results[opposite_pos]["is_auspicious"] = False
                results[opposite_pos]["reason"] = "月命的殺" if not results[opposite_pos]["reason"] else results[opposite_pos]["reason"] + ", 月命的殺"
                results[opposite_pos]["marks"].append("month_star_opposite")

        # 凶方位に fortune_level = "inauspicious" を設定
        for result in results.values():
            if not result["is_auspicious"]:
                result["fortune_level"] = "inauspicious"

        return results

    def get_time_fortune_status(
        self, grid_pattern: Any, params: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """時の運気情報を判定して返す.

        Args:
            grid_pattern: StarGridPattern インスタンス
            params: 吉凶判定に必要なパラメータ
                - zodiac (str): 今年の干支（例: "甲寅"）
                - main_star (int): 本命星の番号（1-9）

        Returns:
            Dict[str, Dict[str, Any]]: 各方位の吉凶状態と具体的なマーク

        Raises:
            ValueError: パラメータが不正な場合
            RuntimeError: 判定処理中に想定外のエラーが発生した場合
        """
        # パラメータの取得と検証
        zodiac = params.get('zodiac', '')
        main_star = params.get('main_star', 0)

        if main_star == 0:
            raise ValueError("Main star is required")

        if not isinstance(zodiac, str):
            raise ValueError("Invalid parameter types")

        # 干支の向かい側の方位を取得（破）
        opposite_zodiac_direction = ""
        try:
            opposite_zodiac_direction = get_opposite_zodiac_direction(zodiac)
        except ValueError as e:
            logger.error(f"Error determining opposite direction from zodiac: {str(e)}")
            logger.warning("Continuing without opposite zodiac direction")

        # 暗剣殺の星を取得
        dark_sword_star = self.get_dark_sword_star(grid_pattern)

        # 各方位の星番号を取得（中央も含める）
        directions = self._build_direction_map(grid_pattern, include_center=True)

        # 各方位の吉凶を判定
        results: Dict[str, Dict[str, Any]] = {}

        # 最初のパス: 基本的な判定を行う
        for direction, star_number in directions.items():
            # デフォルトは吉
            result: Dict[str, Any] = {
                "is_auspicious": True,
                "reason": None,
                "marks": [],
                "is_main_star": False
            }

            # 中央の場合は特別な処理
            if direction == 'center':
                # 中央は暗剣殺判定などはスキップして、本命星判定のみ行う
                if star_number == main_star:
                    result["is_main_star"] = True
                    result["is_auspicious"] = False
                results[direction] = result
                continue

            # 1）暗剣殺の判定
            if dark_sword_star == -1:
                # 中央星が5の場合は暗剣殺判定をスキップ
                result["marks"].append("no_dark_sword_center_five")
            else:
                # 暗剣殺の星を凶とする
                if star_number == dark_sword_star:
                    result["is_auspicious"] = False
                    result["reason"] = "暗剣殺"
                    result["marks"].append("dark_sword")

            # 2）水火殺の判定
            if (star_number == 1 or star_number == 9) and (grid_pattern.south == 1 or grid_pattern.north == 9):
                result["is_auspicious"] = False
                result["reason"] = "水火殺" if not result["reason"] else result["reason"] + ", 水火殺"
                result["marks"].append("water_fire")

            # 3）干支の向かい側（破）の判定
            if direction == opposite_zodiac_direction and opposite_zodiac_direction:
                result["is_auspicious"] = False
                result["reason"] = "破" if not result["reason"] else result["reason"] + ", 破"
                result["marks"].append("opposite_zodiac")

            # 4）本命星の判定
            if star_number == main_star:
                result["is_main_star"] = True

            results[direction] = result

        return results

    @staticmethod
    def get_dark_sword_star(grid_pattern: Any) -> int:
        """暗剣殺（5の反対側）の星番号を取得.

        Args:
            grid_pattern: StarGridPattern インスタンス

        Returns:
            int: 暗剣殺の星番号（1-9）
                 -1: 中央星が5の場合（暗剣殺は存在しない特殊ケース）

        Raises:
            ValueError: 5が見つからない場合や5の反対側がマッピングできない場合
        """
        # 中央星が5の場合は暗剣殺は存在しない（特殊ケース）
        if grid_pattern.center_star == 5:
            return -1

        # 各方位の星番号（中央含む）
        positions = FortuneStatusService._build_direction_map(
            grid_pattern, include_center=True,
        )

        # 5がある方位を特定
        five_position = None
        for position, number in positions.items():
            if number == 5:
                five_position = position
                break

        # 5が見つからない場合（通常ありえない）
        if five_position is None:
            raise ValueError("星盤に五黄土星が存在しません")

        # 反対側の方位を取得
        opposite_position = OPPOSITE_POSITIONS.get(five_position)
        if opposite_position is None:
            raise ValueError(f"五黄土星の反対側の方位がマッピングできません: {five_position}")

        # 反対側の方位の星番号を返す
        return positions.get(opposite_position)

    @staticmethod
    def get_dark_sword_direction(grid_pattern: Any) -> Optional[str]:
        """暗剣殺の方位を取得する.

        Args:
            grid_pattern: StarGridPattern インスタンス

        Returns:
            暗剣殺の方位（"north", "northeast"など）。存在しない場合はNone。
        """
        try:
            dark_sword_star = FortuneStatusService.get_dark_sword_star(grid_pattern)
            if dark_sword_star == -1:
                return None

            directions = FortuneStatusService._build_direction_map(grid_pattern)
            for direction, star in directions.items():
                if star == dark_sword_star:
                    return direction

            return None

        except ValueError:
            return None

    # ──────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────

    @staticmethod
    def _build_direction_map(
        grid_pattern: Any, *, include_center: bool = False,
    ) -> Dict[str, int]:
        """grid_pattern オブジェクトから方位→星番号マップを構築."""
        direction_map: Dict[str, int] = {
            'north': grid_pattern.north,
            'northeast': grid_pattern.northeast,
            'east': grid_pattern.east,
            'southeast': grid_pattern.southeast,
            'south': grid_pattern.south,
            'southwest': grid_pattern.southwest,
            'west': grid_pattern.west,
            'northwest': grid_pattern.northwest,
        }
        if include_center:
            direction_map['center'] = grid_pattern.center_star
        return direction_map

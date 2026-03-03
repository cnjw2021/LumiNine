"""PowerStoneMatchingEngine — 3-Layer 파워스톤 매칭 엔진.

3단계 추천 알고리즘:
  Layer 1: 기본석 (본명성 → 오행 → 기본석)
  Layer 2: 월운석 (최적 길방위 → 오행 → 월운석)
  Layer 3: 호신석 (최악 흉살 방위 → 상극 오행 → 호신석)

설계서 참조: §4-2 PowerStoneMatchingEngine
"""
from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

from apps.ninestarki.domain.exceptions import (
    NoAuspiciousDirectionError,
    PowerStoneMatchingError,
)
from apps.ninestarki.domain.repositories.powerstone_repository_interface import (
    IPowerStoneRepository,
)
from apps.ninestarki.domain.services.interfaces.gogyo_service_interface import (
    IGogyoService,
)
from apps.ninestarki.domain.services.interfaces.powerstone_matching_engine_interface import (
    IPowerStoneMatchingEngine,
)
from apps.ninestarki.domain.value_objects.gogyo import Gogyo, GogyoRelation
from apps.ninestarki.domain.value_objects.powerstone import (
    PowerStone,
    PowerStoneResult,
    StoneRecommendation,
)


# ── 방위 고정 우선순위 (설계서 §4-2 참조) ─────────────────
_DIRECTION_PRIORITY: Dict[str, int] = {
    "south": 0, "east": 1, "southeast": 2, "southwest": 3,
    "north": 4, "west": 5, "northeast": 6, "northwest": 7,
}

# ── 흉살 위험도 순위표 (설계서 §4-2 참조) ─────────────────
# 값이 작을수록 위험
_THREAT_SEVERITY: Dict[str, int] = {
    "five_yellow": 1,       # 五黄殺
    "dark_sword": 2,        # 暗剣殺
    "main_star": 3,         # 本命殺
    "month_star": 4,        # 月命殺
    "water_fire": 5,        # 水火殺
    "opposite_zodiac": 6,   # 破
    "bad_star": 7,          # 凶方星
    "compatibility_matrix": 7,  # 凶方星 (direction-fortune source alias)
    "main_opposite": 8,     # 本命的殺
    "main_star_opposite": 8,    # 本命的殺 (direction-fortune source alias)
    "month_opposite": 9,    # 月命的殺
    "month_star_opposite": 9,   # 月命的殺 (direction-fortune source alias)
}


class PowerStoneMatchingEngine(IPowerStoneMatchingEngine):
    """3-Layer 파워스톤 매칭 엔진.

    DI를 통해 GogyoService, PowerStoneRepository 를 주입받는다.
    """

    def __init__(
        self,
        gogyo_service: IGogyoService,
        stone_repo: IPowerStoneRepository,
    ) -> None:
        self._gogyo = gogyo_service
        self._repo = stone_repo

    # ═══════════════════════════════════════════════════
    # 퍼사드 메서드
    # ═══════════════════════════════════════════════════

    def recommend(
        self,
        main_star: int,
        directions: Dict[str, Any],
    ) -> PowerStoneResult:
        """3-Layer 추천 실행."""
        used_ids: Set[str] = set()

        base = self._layer1_base_stone(main_star, used_ids)
        monthly = self._layer2_monthly_stone(main_star, directions, used_ids)
        protect = self._layer3_protection_stone(directions, used_ids)

        return PowerStoneResult(
            base_stone=base, monthly_stone=monthly, protection_stone=protect,
        )

    # ═══════════════════════════════════════════════════
    # Layer 1: 기본석 (본명성 → 오행 → 기본석)
    # ═══════════════════════════════════════════════════

    def _layer1_base_stone(
        self, main_star: int, used: Set[str],
    ) -> StoneRecommendation:
        """본명성 → 기본석 결정."""
        stone = self._repo.get_base_stone_for_star(main_star)
        used.add(stone.id)
        return StoneRecommendation(
            stone=stone,
            layer="base",
            gogyo=stone.gogyo,
            reason_key="reason.base",
            reason_params={
                "star_name": str(main_star),
                "meaning": f"gogyo.{stone.gogyo.value}",
            },
        )

    # ═══════════════════════════════════════════════════
    # Layer 2: 월운석 (최적 길방위 → 오행 → 월운석)
    # ═══════════════════════════════════════════════════

    def _layer2_monthly_stone(
        self,
        main_star: int,
        directions: Dict[str, Any],
        used: Set[str],
    ) -> StoneRecommendation:
        """최적 길방위 선택 → 오행 → 월운석 결정.

        알고리즘:
          1. is_auspicious == True 인 방위를 필터링
          2. 본명성-오행과의 상성으로 정렬 (SOJO > HIWA > SOKOKU)
          3. 동순위 → 방위 고정 우선순위
          4. 1순위 방위의 오행 → 월운석 오행
        """
        main_gogyo = self._gogyo.star_to_gogyo(main_star)

        # 1. 길방위 필터링
        auspicious = self._filter_auspicious(directions)
        if not auspicious:
            raise NoAuspiciousDirectionError(
                "길방위가 하나도 없어 월운석을 결정할 수 없습니다.",
            )

        # 2-3. 상성 + 방위 우선순위로 정렬 → 최적 방위 선택
        best_direction = self._select_best_direction(auspicious, main_gogyo)
        direction_gogyo = self._gogyo.direction_to_gogyo(best_direction)

        # 4. 월운석 선택 (중복 회피)
        stone = self._pick_stone(direction_gogyo, used)
        used.add(stone.id)

        return StoneRecommendation(
            stone=stone,
            layer="monthly",
            gogyo=direction_gogyo,
            reason_key="reason.monthly",
            reason_params={
                "direction": f"direction.{best_direction}",
                "element": f"gogyo.{direction_gogyo.value}",
            },
            direction=best_direction,
        )

    # ═══════════════════════════════════════════════════
    # Layer 3: 호신석 (최악 흉살 → 상극 오행 → 호신석)
    # ═══════════════════════════════════════════════════

    def _layer3_protection_stone(
        self,
        directions: Dict[str, Any],
        used: Set[str],
    ) -> StoneRecommendation:
        """최악 흉살 방위 → 상극 오행 → 호신석 결정.

        알고리즘:
          1. 각 방위의 흉살 목록에서 최대 위험도 산출
          2. 가장 위험한 방위 + 흉살 결정
          3. 상극 오행으로 억제 오행 결정
          4. 호신석 선택 (중복 회피)
        """
        worst_direction, worst_threat = self._find_worst_threat(directions)
        direction_gogyo = self._gogyo.direction_to_gogyo(worst_direction)
        counter_gogyo = self._gogyo.get_counter_gogyo(direction_gogyo)

        stone = self._pick_stone(counter_gogyo, used)
        used.add(stone.id)

        return StoneRecommendation(
            stone=stone,
            layer="protection",
            gogyo=counter_gogyo,
            reason_key="reason.protection",
            reason_params={
                "threat": f"threat.{worst_threat}",
                "direction": f"direction.{worst_direction}",
                "threat_element": f"gogyo.{direction_gogyo.value}",
                "counter_element": f"gogyo.{counter_gogyo.value}",
            },
            direction=worst_direction,
            threat_mark=worst_threat,
        )

    # ═══════════════════════════════════════════════════
    # 유틸리티 메서드
    # ═══════════════════════════════════════════════════

    def _filter_auspicious(
        self, directions: Dict[str, Any],
    ) -> List[str]:
        """길방위(is_auspicious=True) 필터링."""
        return [
            name
            for name, info in directions.items()
            if info.get("is_auspicious") is True
        ]

    def _select_best_direction(
        self,
        auspicious: List[str],
        main_gogyo: Gogyo,
    ) -> str:
        """길방위를 상성 + 방위 우선순위로 정렬하여 최적 방위 반환."""

        # 상성 정렬 키: SOJO(0) > HIWA(1) > SOKOKU(2)
        relation_order = {
            GogyoRelation.SOJO: 0,
            GogyoRelation.HIWA: 1,
            GogyoRelation.SOKOKU: 2,
        }

        def sort_key(direction: str) -> Tuple[int, int]:
            dir_gogyo = self._gogyo.direction_to_gogyo(direction)
            relation = self._gogyo.get_relation(main_gogyo, dir_gogyo)
            return (
                relation_order.get(relation, 99),
                _DIRECTION_PRIORITY.get(direction, 99),
            )

        return min(auspicious, key=sort_key)

    def _find_worst_threat(
        self, directions: Dict[str, Any],
    ) -> Tuple[str, str]:
        """가장 위험한 흉살 방위 + 흉살 코드 반환.

        Returns:
            (방위명, 흉살 코드) 튜플
        """
        worst_direction = ""
        worst_threat = ""
        worst_severity = 999

        for name, info in directions.items():
            marks = info.get("marks", [])
            for mark in marks:
                mark_code = mark if isinstance(mark, str) else mark.get("code", "")
                severity = _THREAT_SEVERITY.get(mark_code, 999)
                if severity < worst_severity:
                    worst_severity = severity
                    worst_threat = mark_code
                    worst_direction = name
                elif severity == worst_severity:
                    # 동순위 → 방위 우선순위
                    if _DIRECTION_PRIORITY.get(name, 99) < _DIRECTION_PRIORITY.get(
                        worst_direction, 99
                    ):
                        worst_direction = name
                        worst_threat = mark_code

        if not worst_threat:
            raise PowerStoneMatchingError(
                "흉살 정보를 찾을 수 없습니다.",
                code="NO_THREAT_FOUND",
                status=422,
            )

        return worst_direction, worst_threat

    def _pick_stone(self, gogyo: Gogyo, used: Set[str]) -> PowerStone:
        """주석 우선 선택, used 에 포함되면 부석으로 대체."""
        primary = self._repo.get_primary_by_gogyo(gogyo)
        if primary.id not in used:
            return primary

        secondaries = self._repo.get_secondaries_by_gogyo(gogyo)
        for secondary in secondaries:
            if secondary.id not in used:
                return secondary

        # 모든 스톤이 사용된 경우 (극히 드문 에지 케이스)
        raise PowerStoneMatchingError(
            f"오행 '{gogyo.value}' 의 사용 가능한 스톤이 없습니다.",
            code="ALL_STONES_USED",
            status=500,
        )

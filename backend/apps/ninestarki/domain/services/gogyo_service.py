"""GogyoService — 오행 판별·상극 유틸리티 (SRP).

책임: 오행 관련 순수 비즈니스 로직만 담당. 외부 I/O 없음.
SSoT: STAR_TO_GOGYO, DIRECTION_TO_GOGYO, SOKOKU_TABLE 매핑 테이블.
"""
from __future__ import annotations

from typing import Dict, Final

from apps.ninestarki.domain.exceptions import PowerStoneMatchingError
from apps.ninestarki.domain.services.interfaces.gogyo_service_interface import IGogyoService
from apps.ninestarki.domain.value_objects.gogyo import Gogyo, GogyoRelation


class GogyoService(IGogyoService):
    """오행(五行) 판별·상극 유틸리티 서비스."""

    # ── 매핑 테이블 (SSoT) ────────────────────────────────────
    STAR_TO_GOGYO: Final[Dict[int, Gogyo]] = {
        1: Gogyo.WATER, 2: Gogyo.EARTH, 3: Gogyo.WOOD,
        4: Gogyo.WOOD,  5: Gogyo.EARTH, 6: Gogyo.METAL,
        7: Gogyo.METAL, 8: Gogyo.EARTH, 9: Gogyo.FIRE,
    }

    DIRECTION_TO_GOGYO: Final[Dict[str, Gogyo]] = {
        "north": Gogyo.WATER, "northeast": Gogyo.EARTH,
        "east": Gogyo.WOOD,   "southeast": Gogyo.WOOD,
        "south": Gogyo.FIRE,  "southwest": Gogyo.EARTH,
        "west": Gogyo.METAL,  "northwest": Gogyo.METAL,
    }

    # ── 상극 테이블 (SSoT) ────────────────────────────────────
    # key: 억제 대상, value: key를 극하는(억제하는) 오행
    SOKOKU_TABLE: Final[Dict[Gogyo, Gogyo]] = {
        Gogyo.WATER: Gogyo.EARTH,   # 土剋水
        Gogyo.WOOD:  Gogyo.METAL,   # 金剋木
        Gogyo.FIRE:  Gogyo.WATER,   # 水剋火
        Gogyo.EARTH: Gogyo.WOOD,    # 木剋土
        Gogyo.METAL: Gogyo.FIRE,    # 火剋金
    }

    # ── 상생 테이블 (SOJO) ────────────────────────────────────
    # key: 생하는 오행, value: 생을 받는 오행
    _SOJO_TABLE: Final[Dict[Gogyo, Gogyo]] = {
        Gogyo.WOOD:  Gogyo.FIRE,    # 木生火
        Gogyo.FIRE:  Gogyo.EARTH,   # 火生土
        Gogyo.EARTH: Gogyo.METAL,   # 土生金
        Gogyo.METAL: Gogyo.WATER,   # 金生水
        Gogyo.WATER: Gogyo.WOOD,    # 水生木
    }

    # ── 공개 메서드 ──────────────────────────────────────────

    def star_to_gogyo(self, star_number: int) -> Gogyo:
        """본명성 번호(1~9) → 대응 오행 변환."""
        gogyo = self.STAR_TO_GOGYO.get(star_number)
        if gogyo is None:
            raise PowerStoneMatchingError(
                f"유효하지 않은 본명성 번호입니다: {star_number} (1~9 범위)",
                code="INVALID_STAR_NUMBER",
                status=422,
            )
        return gogyo

    def direction_to_gogyo(self, direction: str) -> Gogyo:
        """방위 문자열 → 대응 오행 변환."""
        gogyo = self.DIRECTION_TO_GOGYO.get(direction)
        if gogyo is None:
            raise PowerStoneMatchingError(
                f"알 수 없는 방위입니다: {direction}",
                code="UNKNOWN_DIRECTION",
                status=422,
            )
        return gogyo

    def get_relation(self, a: Gogyo, b: Gogyo) -> GogyoRelation:
        """두 오행 간 관계(상생/상극/비화) 판별."""
        if a == b:
            return GogyoRelation.HIWA

        # a 가 b 를 생하거나, b 가 a 를 생하면 상생
        if self._SOJO_TABLE.get(a) == b or self._SOJO_TABLE.get(b) == a:
            return GogyoRelation.SOJO

        # 그 외 → 상극
        return GogyoRelation.SOKOKU

    def get_counter_gogyo(self, target: Gogyo) -> Gogyo:
        """주어진 오행을 극하는(억제하는) 오행 반환."""
        counter = self.SOKOKU_TABLE.get(target)
        if counter is None:
            raise PowerStoneMatchingError(
                f"유효하지 않은 오행입니다: {target}",
                code="INVALID_GOGYO",
                status=422,
            )
        return counter

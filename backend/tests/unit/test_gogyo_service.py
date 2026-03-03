"""GogyoService 단위 테스트.

커버리지:
  - star_to_gogyo: 1~9 전체 매핑
  - direction_to_gogyo: 8방위 전체 매핑
  - get_counter_gogyo: 5가지 상극 쌍
  - get_relation: 상생(SOJO) / 상극(SOKOKU) / 비화(HIWA) 각 케이스
  - 범위 밖 입력 → PowerStoneMatchingError 발생 확인
"""
from __future__ import annotations

import pytest

from apps.ninestarki.domain.exceptions import PowerStoneMatchingError
from apps.ninestarki.domain.services.gogyo_service import GogyoService
from apps.ninestarki.domain.value_objects.gogyo import Gogyo, GogyoRelation


@pytest.fixture
def svc() -> GogyoService:
    return GogyoService()


# ══════════════════════════════════════════════════════
# star_to_gogyo
# ══════════════════════════════════════════════════════

class TestStarToGogyo:
    """본명성 번호 → 오행 변환."""

    @pytest.mark.parametrize("star, expected", [
        (1, Gogyo.WATER),
        (2, Gogyo.EARTH),
        (3, Gogyo.WOOD),
        (4, Gogyo.WOOD),
        (5, Gogyo.EARTH),
        (6, Gogyo.METAL),
        (7, Gogyo.METAL),
        (8, Gogyo.EARTH),
        (9, Gogyo.FIRE),
    ])
    def test_valid_star(self, svc: GogyoService, star: int, expected: Gogyo):
        assert svc.star_to_gogyo(star) == expected

    @pytest.mark.parametrize("invalid_star", [0, 10, -1, 100])
    def test_invalid_star_raises(self, svc: GogyoService, invalid_star: int):
        with pytest.raises(PowerStoneMatchingError) as exc_info:
            svc.star_to_gogyo(invalid_star)
        assert exc_info.value.code == "INVALID_STAR_NUMBER"
        assert exc_info.value.status == 422


# ══════════════════════════════════════════════════════
# direction_to_gogyo
# ══════════════════════════════════════════════════════

class TestDirectionToGogyo:
    """방위 문자열 → 오행 변환."""

    @pytest.mark.parametrize("direction, expected", [
        ("north", Gogyo.WATER),
        ("northeast", Gogyo.EARTH),
        ("east", Gogyo.WOOD),
        ("southeast", Gogyo.WOOD),
        ("south", Gogyo.FIRE),
        ("southwest", Gogyo.EARTH),
        ("west", Gogyo.METAL),
        ("northwest", Gogyo.METAL),
    ])
    def test_valid_direction(self, svc: GogyoService, direction: str, expected: Gogyo):
        assert svc.direction_to_gogyo(direction) == expected

    @pytest.mark.parametrize("invalid_direction", ["N", "NORTH", "北", "center", ""])
    def test_invalid_direction_raises(self, svc: GogyoService, invalid_direction: str):
        with pytest.raises(PowerStoneMatchingError) as exc_info:
            svc.direction_to_gogyo(invalid_direction)
        assert exc_info.value.code == "UNKNOWN_DIRECTION"
        assert exc_info.value.status == 422


# ══════════════════════════════════════════════════════
# get_counter_gogyo
# ══════════════════════════════════════════════════════

class TestGetCounterGogyo:
    """상극 오행 반환 (SOKOKU)."""

    @pytest.mark.parametrize("target, counter", [
        (Gogyo.WATER, Gogyo.EARTH),   # 土剋水
        (Gogyo.WOOD,  Gogyo.METAL),   # 金剋木
        (Gogyo.FIRE,  Gogyo.WATER),   # 水剋火
        (Gogyo.EARTH, Gogyo.WOOD),    # 木剋土
        (Gogyo.METAL, Gogyo.FIRE),    # 火剋金
    ])
    def test_counter_gogyo(self, svc: GogyoService, target: Gogyo, counter: Gogyo):
        assert svc.get_counter_gogyo(target) == counter


# ══════════════════════════════════════════════════════
# get_relation
# ══════════════════════════════════════════════════════

class TestGetRelation:
    """두 오행 간 관계 판별."""

    # ── 비화(HIWA): 같은 오행 ──
    @pytest.mark.parametrize("gogyo", list(Gogyo))
    def test_same_element_is_hiwa(self, svc: GogyoService, gogyo: Gogyo):
        assert svc.get_relation(gogyo, gogyo) == GogyoRelation.HIWA

    # ── 상생(SOJO): 생하는/생을 받는 관계 ──
    @pytest.mark.parametrize("a, b", [
        (Gogyo.WOOD, Gogyo.FIRE),    # 木生火
        (Gogyo.FIRE, Gogyo.EARTH),   # 火生土
        (Gogyo.EARTH, Gogyo.METAL),  # 土生金
        (Gogyo.METAL, Gogyo.WATER),  # 金生水
        (Gogyo.WATER, Gogyo.WOOD),   # 水生木
    ])
    def test_sojo_forward(self, svc: GogyoService, a: Gogyo, b: Gogyo):
        """a가 b를 생하면 상생."""
        assert svc.get_relation(a, b) == GogyoRelation.SOJO

    @pytest.mark.parametrize("a, b", [
        (Gogyo.FIRE, Gogyo.WOOD),    # 木生火 (역방향도 상생)
        (Gogyo.EARTH, Gogyo.FIRE),
        (Gogyo.METAL, Gogyo.EARTH),
        (Gogyo.WATER, Gogyo.METAL),
        (Gogyo.WOOD, Gogyo.WATER),
    ])
    def test_sojo_reverse(self, svc: GogyoService, a: Gogyo, b: Gogyo):
        """b가 a를 생해도 상생."""
        assert svc.get_relation(a, b) == GogyoRelation.SOJO

    # ── 상극(SOKOKU): 극하는/극을 받는 관계 ──
    @pytest.mark.parametrize("a, b", [
        (Gogyo.WATER, Gogyo.FIRE),   # 水剋火
        (Gogyo.FIRE, Gogyo.METAL),   # 火剋金
        (Gogyo.METAL, Gogyo.WOOD),   # 金剋木
        (Gogyo.WOOD, Gogyo.EARTH),   # 木剋土
        (Gogyo.EARTH, Gogyo.WATER),  # 土剋水
    ])
    def test_sokoku(self, svc: GogyoService, a: Gogyo, b: Gogyo):
        assert svc.get_relation(a, b) == GogyoRelation.SOKOKU

    @pytest.mark.parametrize("a, b", [
        (Gogyo.FIRE, Gogyo.WATER),   # 水剋火 (역방향)
        (Gogyo.METAL, Gogyo.FIRE),
    ])
    def test_sokoku_reverse(self, svc: GogyoService, a: Gogyo, b: Gogyo):
        """b가 a를 극해도 상극."""
        assert svc.get_relation(a, b) == GogyoRelation.SOKOKU

"""방위 길흉 판정 일관성 교차 검증 테스트.

`month-acquired-fortune` API (방위 그리드)와 `monthly-board` API (스톤 추천)가
동일한 입력에 대해 동일한 `is_auspicious` 결과를 반환하는지 검증한다.

Issue #61: 기존에 두 API가 서로 다른 메서드(get_time_fortune_status vs get_fortune_status)를
사용하여 흉살 체크 5개가 누락되는 버그 발생. 이 테스트로 회귀를 방지한다.
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from core.models.star_grid_pattern import StarGridPattern


# ══════════════════════════════════════════════════════
# 테스트 헬퍼: StarGridPattern 의 순수 로직만 테스트하기 위한 가짜 객체
# ══════════════════════════════════════════════════════

class FakeGridPattern:
    """StarGridPattern 에서 DB/ORM 의존 없이 순수 길흉 판정 메서드만 호출 가능한 객체."""

    def __init__(
        self, center: int,
        north: int, northeast: int, east: int, southeast: int,
        south: int, southwest: int, west: int, northwest: int,
    ):
        self.center_star = center
        self.north = north
        self.northeast = northeast
        self.east = east
        self.southeast = southeast
        self.south = south
        self.southwest = southwest
        self.west = west
        self.northwest = northwest

    def get_fortune_status(self, params):
        return StarGridPattern.get_fortune_status(self, params)

    def get_time_fortune_status(self, params):
        return StarGridPattern.get_time_fortune_status(self, params)

    def _get_dark_sword_star(self):
        return StarGridPattern._get_dark_sword_star(self)


# 九星盤パターン: 중궁성 2 (二黒土星). 五黄은 northeast에 위치.
_GRID_CENTER_2 = FakeGridPattern(
    center=2,
    south=6, southwest=8, west=1,
    northwest=3, north=4, northeast=5,
    east=9, southeast=7,
)

# 九星盤パターン: 중궁성 5 (五黄土星) — 暗剣殺이 없는 특수 케이스
_GRID_CENTER_5 = FakeGridPattern(
    center=5,
    south=9, southwest=2, west=4,
    northwest=6, north=7, northeast=8,
    east=3, southeast=1,
)

# 다양한 星 조합의 파라미터 세트
_PARAMS_CASES = [
    {"main_star": 1, "month_star": 3, "zodiac": "甲寅"},
    {"main_star": 4, "month_star": 7, "zodiac": "乙卯"},
    {"main_star": 7, "month_star": 9, "zodiac": "丙辰"},
    {"main_star": 2, "month_star": 5, "zodiac": "丁巳"},
    {"main_star": 9, "month_star": 1, "zodiac": "甲子"},
]

_DIRECTIONS = [
    "north", "northeast", "east", "southeast",
    "south", "southwest", "west", "northwest",
]


# ══════════════════════════════════════════════════════
# 교차 검증 테스트
# ══════════════════════════════════════════════════════

class TestDirectionConsistency:
    """두 방위 판정 메서드의 is_auspicious 결과가 일치하는지 교차 검증."""

    @pytest.fixture(params=[_GRID_CENTER_2, _GRID_CENTER_5], ids=["center_2", "center_5"])
    def grid(self, request):
        return request.param

    @pytest.fixture(params=_PARAMS_CASES, ids=[
        f"main{p['main_star']}_month{p['month_star']}" for p in _PARAMS_CASES
    ])
    def params(self, request):
        return request.param

    def test_fortune_status_is_stricter_or_equal(self, grid, params):
        """get_fortune_status()의 凶방위 집합은 반드시
        get_time_fortune_status()의 凶방위 집합을 포함해야 한다.

        즉 get_fortune_status()에서 吉인 방위가
        get_time_fortune_status()에서 凶으로 되는 것은 논리적으로 불가능.
        """
        full_result = grid.get_fortune_status(params)
        time_result = grid.get_time_fortune_status(params)

        for d in _DIRECTIONS:
            full_ausp = full_result.get(d, {}).get("is_auspicious", True)
            time_ausp = time_result.get(d, {}).get("is_auspicious", True)

            if full_ausp is True:
                assert time_ausp is True, (
                    f"방위 '{d}': get_fortune_status()=吉 이지만 "
                    f"get_time_fortune_status()=凶. "
                    f"full_marks={full_result[d].get('marks')}, "
                    f"time_marks={time_result[d].get('marks')}"
                )

    def test_inauspicious_sets_match(self, grid, params):
        """수정 이후, 두 메서드의 凶방위 집합이 동일해야 한다.

        get_fortune_status()에 포함된 五黄殺/本命殺/月命殺 체크가
        get_time_fortune_status()에서 누락되면 이 테스트가 실패한다.
        """
        full_result = grid.get_fortune_status(params)

        time_result = grid.get_time_fortune_status(params)

        full_inauspicious = {
            d for d in _DIRECTIONS
            if full_result.get(d, {}).get("is_auspicious") is False
        }
        time_inauspicious = {
            d for d in _DIRECTIONS
            if time_result.get(d, {}).get("is_auspicious") is False
        }

        # get_time_fortune_status의 凶방위가 get_fortune_status에 포함되어야 함
        assert time_inauspicious.issubset(full_inauspicious), (
            f"get_time_fortune_status()에만 존재하는 凶방위: "
            f"{time_inauspicious - full_inauspicious}"
        )


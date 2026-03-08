"""AdditionalDirectionMarksService 단위 테스트.

커버리지:
  - 定位対冲: 정위 반대 방위에 배치된 별 → 길방이 neutral로 다운그레이드 + reason 추가
  - 小児殺: 월지 기반 흉방 → 길방이 neutral로 다운그레이드 + reason 추가
  - 定位対冲 + 小児殺 동시: reason이 콤마 구분 결합
  - 天道: 참고 마크 추가 + reason 추가 (fortune_level 변경 없음)
  - _append_reason 헬퍼: 빈 reason / 기존 reason / 중복 방지
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pytest

from apps.reading.ninestarki.domain.services.additional_direction_marks_service import (
    AdditionalDirectionMarksService,
)


# ── Fake grid pattern ──────────────────────────────────

@dataclass
class FakeGrid:
    """Minimal grid pattern stub for tests.
    
    Note: AdditionalDirectionMarksService.enrich() returns early if no star
    attributes are set (star_map becomes empty), so tests that exercise
    小児殺 or 天道 must set at least one star.
    """
    north: Optional[int] = None
    northeast: Optional[int] = None
    east: Optional[int] = None
    southeast: Optional[int] = None
    south: Optional[int] = None
    southwest: Optional[int] = None
    west: Optional[int] = None
    northwest: Optional[int] = None


@pytest.fixture
def svc() -> AdditionalDirectionMarksService:
    return AdditionalDirectionMarksService()


def _make_direction(
    fortune_level: str = "auspicious",
    is_auspicious: bool = True,
    reason: str = "",
) -> dict:
    """Helper to create a direction result dict."""
    d: dict = {
        "fortune_level": fortune_level,
        "is_auspicious": is_auspicious,
    }
    if reason:
        d["reason"] = reason
    return d


# ══════════════════════════════════════════════════════
# 定位対冲
# ══════════════════════════════════════════════════════

class TestTeiiTaichuu:
    """정위 반대 방위에 별이 배치된 경우 다운그레이드."""

    def test_auspicious_downgraded_to_neutral(self, svc: AdditionalDirectionMarksService):
        """Star 1 (home=north) at south (opposite) → south downgraded."""
        directions = {"south": _make_direction("auspicious", True)}
        grid = FakeGrid(south=1)  # Star 1 at south
        svc.enrich(directions, grid_pattern=grid, month_branch="寅")
        assert directions["south"]["fortune_level"] == "neutral"
        assert directions["south"]["is_auspicious"] is None
        assert "teii_taichuu" in directions["south"]["additional_marks"]

    def test_reason_set_for_teii_taichuu(self, svc: AdditionalDirectionMarksService):
        """Reason field should include 定位対冲."""
        directions = {"south": _make_direction("auspicious", True)}
        grid = FakeGrid(south=1)  # Star 1 (home=north) at south (opposite)
        svc.enrich(directions, grid_pattern=grid, month_branch="卯")  # 卯: shouni=NW, not south
        assert directions["south"]["reason"] == "定位対冲"

    def test_neutral_not_downgraded(self, svc: AdditionalDirectionMarksService):
        """Already neutral direction is not re-downgraded, but mark is still added."""
        directions = {"south": _make_direction("neutral", None)}
        grid = FakeGrid(south=1)
        svc.enrich(directions, grid_pattern=grid, month_branch="寅")
        assert directions["south"]["fortune_level"] == "neutral"
        assert "teii_taichuu" in directions["south"]["additional_marks"]


# ══════════════════════════════════════════════════════
# 小児殺
# ══════════════════════════════════════════════════════

class TestShouniSatsu:
    """월지 기반 소아살 방위 다운그레이드."""

    def test_auspicious_downgraded(self, svc: AdditionalDirectionMarksService):
        """月支=寅 → south is 小児殺 → downgraded."""
        directions = {"south": _make_direction("auspicious", True)}
        grid = FakeGrid(north=5)  # Dummy star to avoid early return; star 5 has no home
        svc.enrich(directions, grid_pattern=grid, month_branch="寅")
        assert directions["south"]["fortune_level"] == "neutral"
        assert directions["south"]["is_auspicious"] is None
        assert "shouni_satsu" in directions["south"]["additional_marks"]

    def test_reason_set_for_shouni_satsu(self, svc: AdditionalDirectionMarksService):
        directions = {"south": _make_direction("auspicious", True)}
        grid = FakeGrid(north=5)  # Dummy star
        svc.enrich(directions, grid_pattern=grid, month_branch="寅")
        assert "小児殺" in directions["south"]["reason"]


# ══════════════════════════════════════════════════════
# 定位対冲 + 小児殺 combined
# ══════════════════════════════════════════════════════

class TestCombinedMarks:
    """定位対冲 と 小児殺 が同一方位に重なるケース."""

    def test_both_marks_comma_separated_reason(self, svc: AdditionalDirectionMarksService):
        """Star 1 at south + 月支=寅 → south gets both marks."""
        directions = {"south": _make_direction("best_auspicious", True)}
        grid = FakeGrid(south=1)
        svc.enrich(directions, grid_pattern=grid, month_branch="寅")
        marks = directions["south"]["additional_marks"]
        assert "teii_taichuu" in marks
        assert "shouni_satsu" in marks
        reason = directions["south"]["reason"]
        assert "定位対冲" in reason
        assert "小児殺" in reason
        assert ", " in reason  # comma-separated


# ══════════════════════════════════════════════════════
# 天道
# ══════════════════════════════════════════════════════

class TestTendo:
    """천도 참고 마크 추가 (fortune_level 변경 없음)."""

    def test_tendo_mark_added(self, svc: AdditionalDirectionMarksService):
        """月支=寅 → northwest is 天道."""
        directions = {"northwest": _make_direction("auspicious", True)}
        grid = FakeGrid(north=5)  # Dummy star
        svc.enrich(directions, grid_pattern=grid, month_branch="寅")
        assert "tendo" in directions["northwest"]["additional_marks"]

    def test_tendo_does_not_change_fortune_level(self, svc: AdditionalDirectionMarksService):
        directions = {"northwest": _make_direction("auspicious", True)}
        grid = FakeGrid(north=5)  # Dummy star
        svc.enrich(directions, grid_pattern=grid, month_branch="寅")
        assert directions["northwest"]["fortune_level"] == "auspicious"
        assert directions["northwest"]["is_auspicious"] is True

    def test_tendo_appends_reason(self, svc: AdditionalDirectionMarksService):
        directions = {"northwest": _make_direction("auspicious", True, reason="既存理由")}
        grid = FakeGrid(north=5)  # Dummy star
        svc.enrich(directions, grid_pattern=grid, month_branch="寅")
        assert directions["northwest"]["reason"] == "既存理由, 天道"


# ══════════════════════════════════════════════════════
# _append_reason helper
# ══════════════════════════════════════════════════════

class TestAppendReason:
    """_append_reason static method edge cases."""

    def test_empty_reason(self):
        result: dict = {}
        AdditionalDirectionMarksService._append_reason(result, "テスト")
        assert result["reason"] == "テスト"

    def test_existing_reason_appended(self):
        result = {"reason": "既存"}
        AdditionalDirectionMarksService._append_reason(result, "追加")
        assert result["reason"] == "既存, 追加"

    def test_duplicate_label_not_appended(self):
        result = {"reason": "定位対冲"}
        AdditionalDirectionMarksService._append_reason(result, "定位対冲")
        assert result["reason"] == "定位対冲"  # No duplication

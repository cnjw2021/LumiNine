"""MonthlyDirectionsUseCase 단위 테스트 (Phase 1 Foundation).

Stub Repository / Stub Domain Service 를 사용하며 외부 DB 의존이 없다.
커버리지:
  - 단일 setsu_index 조회
  - 전체 12개월 조회 (target_month=None)
  - 절입일 미존재(period_start=None) 시 skip 동작
  - 연반 정보 미존재 시 YearInfoNotFoundError
"""
from __future__ import annotations

import pytest
from datetime import date
from typing import Any, Optional
from apps.ninestarki.use_cases.monthly_directions_use_case import MonthlyDirectionsUseCase
from apps.ninestarki.domain.services.monthly_board_domain_service import MonthlyBoardResult
from apps.ninestarki.domain.services.five_elements_fortune_service import FiveElementsFortuneService
from apps.ninestarki.domain.services.additional_direction_marks_service import AdditionalDirectionMarksService
from apps.ninestarki.domain.exceptions import YearInfoNotFoundError


# ══════════════════════════════════════════════════════
# Stubs
# ══════════════════════════════════════════════════════

class _StubGridPattern:
    def get_fortune_status(self, params: dict) -> dict:
        return {"north": "auspicious", "south": "inauspicious"}

    def to_dict(self):
        return {}


def _make_board_result(setsu_idx: int) -> MonthlyBoardResult:
    return MonthlyBoardResult(
        setsu_month_index=setsu_idx,
        center_star=((8 - setsu_idx) % 9) + 1,  # 임의 역행값
        grid_pattern=_StubGridPattern(),
        month_stem="丙",
        month_branch="寅",
        month_zodiac="丙寅",
        period_start=date(2026, 2, 4),
        period_end=date(2026, 3, 4),
    )


class _StubYearStarService:
    """연반 정보를 반환하는 Stub."""

    def __init__(self, star_number: int = 4, zodiac: str = "甲子"):
        self._star_number = star_number
        self._zodiac = zodiac

    def get_year_star_info(self, year: int) -> Optional[dict]:
        return {"star_number": self._star_number, "zodiac": self._zodiac}


class _StubYearStarServiceEmpty:
    def get_year_star_info(self, year: int) -> Optional[dict]:
        return None


class _StubMonthlyBoardService:
    """절입일 취득 + 월반 편성을 대행하는 Stub."""

    def __init__(self, missing_setsu_indices: list[int] | None = None):
        self._missing = set(missing_setsu_indices or [])

    def get_period_start_for_setsu(self, year: int, setsu_index: int) -> Optional[date]:
        if setsu_index in self._missing:
            return None
        # 지적 사항 [5] 대응: 12번(丑月) 절입은 다음 해 1월 5일경(小寒)
        if setsu_index == 12:
            return date(year + 1, 1, 5)
        return date(year, max(1, min(12, setsu_index + 1)), 4)

    def get_monthly_board(self, target_date: date) -> MonthlyBoardResult:
        # setsu_index 역산 로직 (도메인 규칙에 맞춘 단순화 버전):
        # - 12월 大雪(setsu=11) 기간은 다음 해 1/4까지 이어짐
        # - 1월 1~4일: 전년 12월(子月, setsu_index=11)에 속함
        # - 1월 5일 이후: 小寒(setsu_index=12) 시작
        # - 그 외 달: 단순히 month-1 로 매핑 (테스트용 Stub 규칙)
        if target_date.month == 1 and target_date.day < 5:
            idx = 11
        elif target_date.month == 1:
            idx = 12
        else:
            idx = target_date.month - 1
        return _make_board_result(idx)


# ══════════════════════════════════════════════════════
# Tests
# ══════════════════════════════════════════════════════

class TestMonthlyDirectionsUseCaseSingleMonth:
    """단일 setsu_index 조회 테스트."""

    @pytest.fixture
    def use_case(self):
        return MonthlyDirectionsUseCase(
            year_star_service=_StubYearStarService(),
            monthly_board_service=_StubMonthlyBoardService(),
            five_elements_service=FiveElementsFortuneService(),
            additional_marks_service=AdditionalDirectionMarksService(),
        )

    def test_returns_dict_with_required_keys(self, use_case):
        result = use_case.execute(main_star=4, month_star=7, target_year=2026, target_month=3)
        assert "main_star" in result
        assert "month_star" in result
        assert "target_year" in result
        assert "monthly_boards" in result
        assert "year_center_star" in result
        assert "year_zodiac" in result

    def test_single_month_returns_one_board(self, use_case):
        result = use_case.execute(main_star=4, month_star=7, target_year=2026, target_month=3)
        boards = result["monthly_boards"]
        assert len(boards) == 1
        assert "setsu_month_3" in boards

    def test_board_has_direction_data(self, use_case):
        result = use_case.execute(main_star=4, month_star=7, target_year=2026, target_month=3)
        board = result["monthly_boards"]["setsu_month_3"]
        assert "directions" in board
        assert "center_star" in board
        assert "month_zodiac" in board
        assert "period_start" in board
        assert "period_end" in board


class TestMonthlyDirectionsUseCaseAllMonths:
    """전체 12개월 조회 테스트 (target_month=None)."""

    @pytest.fixture
    def use_case(self):
        return MonthlyDirectionsUseCase(
            year_star_service=_StubYearStarService(),
            monthly_board_service=_StubMonthlyBoardService(),
            five_elements_service=FiveElementsFortuneService(),
            additional_marks_service=AdditionalDirectionMarksService(),
        )

    def test_all_12_months_returned(self, use_case):
        result = use_case.execute(main_star=4, month_star=7, target_year=2026, target_month=None)
        boards = result["monthly_boards"]
        assert len(boards) == 12
        for idx in range(1, 13):
            assert f"setsu_month_{idx}" in boards


class TestMonthlyDirectionsUseCaseMissingSetsuDate:
    """절입일 미존재 시 해당 월 skip 동작 테스트."""

    @pytest.fixture
    def use_case(self):
        # setsu_index=5, 9 가 DB에 없는 상황
        return MonthlyDirectionsUseCase(
            year_star_service=_StubYearStarService(),
            monthly_board_service=_StubMonthlyBoardService(missing_setsu_indices=[5, 9]),
            five_elements_service=FiveElementsFortuneService(),
            additional_marks_service=AdditionalDirectionMarksService(),
        )

    def test_missing_setsu_skipped(self, use_case):
        result = use_case.execute(main_star=4, month_star=7, target_year=2026, target_month=None)
        boards = result["monthly_boards"]
        assert "setsu_month_5" not in boards
        assert "setsu_month_9" not in boards
        assert len(boards) == 10  # 12 - 2개 skip

    def test_present_months_still_included(self, use_case):
        result = use_case.execute(main_star=4, month_star=7, target_year=2026, target_month=None)
        boards = result["monthly_boards"]
        for idx in [1, 2, 3, 4, 6, 7, 8, 10, 11, 12]:
            assert f"setsu_month_{idx}" in boards


class TestMonthlyDirectionsUseCaseMissingYearInfo:
    """연반 정보 미존재 시 YearInfoNotFoundError."""

    @pytest.fixture
    def use_case(self):
        return MonthlyDirectionsUseCase(
            year_star_service=_StubYearStarServiceEmpty(),
            monthly_board_service=_StubMonthlyBoardService(),
            five_elements_service=FiveElementsFortuneService(),
            additional_marks_service=AdditionalDirectionMarksService(),
        )

    def test_raises_year_info_not_found_error_when_year_info_missing(self, use_case):
        with pytest.raises(YearInfoNotFoundError, match="연반 정보"):
            use_case.execute(main_star=4, month_star=7, target_year=2026, target_month=1)

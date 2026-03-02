"""월반(月盤) 기반 시스템 단위 테스트 (Phase 1 Foundation).

pytest 스타일을 따르며, 외부 DB/인프라 의존 없이 Stub 레포지토리를 사용한다.
설계서: docs/monthly-direction-with-powerstone.md 참조
"""
from __future__ import annotations

import pytest
from datetime import date

from apps.ninestarki.domain.services.monthly_board_domain_service import (
    MonthlyBoardDomainService,
    MonthlyBoardResult,
)


# ══════════════════════════════════════════════════════
# Stubs
# ══════════════════════════════════════════════════════

class _StubSolarTerm:
    """SolarTerm エンティティのスタブ."""
    def __init__(self, year: int, month: int, solar_terms_date: date, zodiac: str = "甲子", star_number: int = 1):
        self.year = year
        self.month = month
        self.solar_terms_date = solar_terms_date
        self.zodiac = zodiac
        self.star_number = star_number
        self.solar_terms_name = "節"
        self.solar_terms_time = None


class _StubSolarTermsRepo:
    """절기 데이터를 메모리에 보유하는 Stub ISolarTermsRepository.

    MonthlyBoardDomainService 가 호출하는 메서드만 구현한다:
      - get_yearly_terms(year)
      - get_term_by_month(year, month)
    """

    def __init__(self, terms: list[_StubSolarTerm]):
        self._terms = terms

    def get_yearly_terms(self, year: int):
        return [t for t in self._terms if t.year == year]

    def get_term_by_month(self, year: int, month: int):
        for t in self._terms:
            if t.year == year and t.month == month:
                return t
        return None

    def get_spring_start(self, year: int):
        for t in self._terms:
            if t.year == year and t.month == 2:
                return t
        return None


class _StubGridPattern:
    def __init__(self, center_star: int):
        self.center_star = center_star

    def to_dict(self):
        return {"center_star": self.center_star}

    def get_fortune_status(self, params):
        return {}


class _StubStarGridPatternRepo:
    def get_by_center_star(self, center_star: int):
        return _StubGridPattern(center_star)




# ══════════════════════════════════════════════════════
# Tests — MonthlyBoardDomainService
# ══════════════════════════════════════════════════════

def _make_solar_terms_repo() -> _StubSolarTermsRepo:
    """Year 2024~2027 stub 절기 데이터를 생성한다.

    실제 SolarTermsRepository 구조와 동일하게:
      - 해당 연도의 그레고리력 2~12월 절기 (month 2=立春 … month 12=大雪)
      - 다음해 1월 절기 (month 1=小寒)
    로 구성한다. (AuspiciousCalendarService.get_solar_terms_for_year() 기준)
    """
    terms = []
    for year in [2024, 2025, 2026, 2027]:
        # 2~12월: 각 월 4일을 절입일로 설정
        for month in range(2, 13):
            solar_date = date(year, month, 4)
            zt = "甲子" if year == 2026 else "乙丑" if year == 2025 else "癸卯"
            terms.append(_StubSolarTerm(year, month, solar_date, zodiac=zt, star_number=month))
        # 다음해 1월(小寒) 절기를 당해 연도 레코드로는 넣지 않는다 (next_year 의 것)

    # next_year 의 1월 절기(小寒) → setsu_index=12 에 해당
    for year in [2025, 2026, 2027, 2028]:
        solar_date = date(year, 1, 5)
        zt = "甲子" if year == 2026 else "乙丑" if year == 2025 else "癸卯"
        terms.append(_StubSolarTerm(year, 1, solar_date, zodiac=zt, star_number=1))

    return _StubSolarTermsRepo(terms)


class TestMonthlyBoardDomainService:
    """MonthlyBoardDomainService の結合テスト (Stub Repository 사용)."""

    @pytest.fixture
    def service(self):
        return MonthlyBoardDomainService(
            solar_terms_repo=_make_solar_terms_repo(),
            star_grid_repo=_StubStarGridPatternRepo(),
        )

    def test_returns_monthly_board_result(self, service):
        result = service.get_monthly_board(
            target_date=date(2026, 2, 5),   # 2026년 寅月 절입일 직후
        )
        assert isinstance(result, MonthlyBoardResult)
        assert 1 <= result.center_star <= 9

    def test_grid_pattern_assembled(self, service):
        result = service.get_monthly_board(
            target_date=date(2026, 2, 5),
        )
        assert result.grid_pattern is not None
        # Stub returns _StubGridPattern whose center_star equals result.center_star
        assert result.grid_pattern.center_star == result.center_star

    def test_month_zodiac_format(self, service):
        result = service.get_monthly_board(
            target_date=date(2026, 2, 5),
        )
        assert len(result.month_zodiac) == 2
        assert result.month_zodiac[0] in "甲乙丙丁戊己庚辛壬癸"
        assert result.month_zodiac[1] in "子丑寅卯辰巳午未申酉戌亥"

    def test_period_start_before_period_end(self, service):
        result = service.get_monthly_board(
            target_date=date(2026, 2, 5),
        )
        assert result.period_start <= result.period_end


    def test_to_dict_has_required_keys(self, service):
        result = service.get_monthly_board(
            target_date=date(2026, 2, 5),
        )
        d = result.to_dict()
        required_keys = {
            "setsu_month_index", "center_star", "month_stem", "month_branch",
            "month_zodiac", "period_start", "period_end", "grid_pattern",
        }
        assert required_keys.issubset(d.keys())

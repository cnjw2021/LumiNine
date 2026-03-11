"""월반(月盤) 기반 시스템 단위 테스트 (Phase 1 Foundation).

pytest 스타일을 따르며, 외부 DB/인프라 의존 없이 Stub 레포지토리를 사용한다.
설계서: docs/monthly-direction-with-powerstone.md 참조
"""
from __future__ import annotations

import pytest
from datetime import date

from apps.reading.ninestarki.domain.services.monthly_board_domain_service import (
    MonthlyBoardDomainService,
    MonthlyBoardResult,
)
from apps.reading.ninestarki.domain.value_objects.star_grid_pattern_vo import StarGridPatternVO


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


class _StubStarGridPatternRepo:
    """StarGridPattern リポジトリのスタブ — StarGridPatternVO を返す."""
    def get_by_center_star(self, center_star: int):
        return StarGridPatternVO(
            center_star=center_star,
            north=1, northeast=2, east=3, southeast=4,
            south=5, southwest=6, west=7, northwest=8,
        )

class _StubMonthlyDirection:
    """MonthlyDirections エンティティのスタブ."""
    def __init__(self, group_id: int, month: int, center_star: int):
        self.group_id = group_id
        self.month = month
        self.center_star = center_star


class _StubMonthlyDirectionsRepo:
    """monthly_directions テーブルの Stub."""

    def __init__(self, directions: list[_StubMonthlyDirection]):
        self._directions = directions

    def get_by_group_and_month(self, group_id: int, month: int):
        for d in self._directions:
            if d.group_id == group_id and d.month == month:
                return d
        return None

    def list_by_group(self, group_id: int):
        return [d for d in self._directions if d.group_id == group_id]

    def list_by_month(self, month: int):
        return [d for d in self._directions if d.month == month]


class _StubSolarStarts:
    """SolarStarts エンティティのスタブ."""
    def __init__(self, year: int, star_number: int, zodiac: str = "丙午"):
        self.year = year
        self.star_number = star_number
        self.zodiac = zodiac


class _StubSolarStartsRepo:
    """solar_starts_data Stub — 年盤中宮星 を提供."""
    def __init__(self, starts: list[_StubSolarStarts]):
        self._starts = starts

    def get_by_year(self, year: int):
        for s in self._starts:
            if s.year == year:
                return s
        return None


def _make_solar_starts_repo() -> _StubSolarStartsRepo:
    """2024~2027 年盤中宮星 stub.

    年盤中宮星の伝統的なパターン:
      2024→3, 2025→2, 2026→1, 2027→9
    """
    return _StubSolarStartsRepo([
        _StubSolarStarts(2024, 3, "甲辰"),
        _StubSolarStarts(2025, 2, "乙巳"),
        _StubSolarStarts(2026, 1, "丙午"),
        _StubSolarStarts(2027, 9, "丁未"),
    ])


def _make_monthly_directions_repo() -> _StubMonthlyDirectionsRepo:
    """Group 1~3, month 1~12 の stub monthly_directions を生成."""
    # Group Feb 開始 center_star (伝統的パターン)
    GROUP_FEB_CENTER = {1: 8, 2: 2, 3: 5}
    directions = []
    for gid in [1, 2, 3]:
        feb_center = GROUP_FEB_CENTER[gid]
        # 月順: 1,2,3,...,12
        for month in range(1, 13):
            # 2月=offset 0, 3月=offset 1, ..., 12月=offset 10, 1月=offset 11
            offset = (month - 2) % 12
            cs = ((feb_center - 1 - offset) % 9) + 1
            directions.append(_StubMonthlyDirection(gid, month, cs))
    return _StubMonthlyDirectionsRepo(directions)



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
            # star_number はドメイン不変条件に合わせて 1~9 にマッピングする
            terms.append(
                _StubSolarTerm(
                    year,
                    month,
                    solar_date,
                    zodiac=zt,
                    star_number=((month - 1) % 9) + 1,
                )
            )
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
            solar_starts_repo=_make_solar_starts_repo(),
            star_grid_repo=_StubStarGridPatternRepo(),
            monthly_directions_repo=_make_monthly_directions_repo(),
        )

    def test_returns_monthly_board_result(self, service):
        result = service.get_monthly_board(
            target_date=date(2026, 2, 5),   # 2026년 寅月 절입일 직후
        )
        assert isinstance(result, MonthlyBoardResult)
        assert 1 <= result.center_star <= 9

    def test_grid_pattern_is_domain_vo(self, service):
        """grid_pattern が StarGridPatternVO ドメイン VO であることを検証する."""
        result = service.get_monthly_board(
            target_date=date(2026, 2, 5),
        )
        assert result.grid_pattern is not None
        assert isinstance(result.grid_pattern, StarGridPatternVO)
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

    def test_center_star_differs_from_solar_terms_star_number(self, service):
        """center_star が solar_terms_data.star_number と異なるケースが存在することを
        検証する回帰テスト。

        年盤中宮星(solar_starts_data.star_number) 経由でグループが決定されるため、
        節気運星(solar_terms_data.star_number) をそのまま使うバグが再発すると、
        この assertion が失敗する。
        """
        # stub: 2026 → year_center_star=1 → group=1
        # Group 1, month=3: offset=(3-2)%12=1, cs=((8-1-1)%9)+1=7
        result = service.get_monthly_board(target_date=date(2026, 3, 5))
        assert result.center_star == 7, (
            "center_star should resolve to 7 for 2026-03 (year_center_star=1→group 1); "
            "if this fails, solar_terms_data.star_number may be used instead of "
            "solar_starts_data.star_number for group determination"
        )

    def test_center_star_before_lichun_uses_previous_year_group(self, service):
        """立春より前の日付で lookup_year が前年に繰り下がるケースの回帰テスト。

        2026-01-10 のような 立春 前の日付では、service は前年の
        年盤中宮星(solar_starts_data) からグループを決定する必要がある。

        stub 実装では:
          - lookup_year=2025 の year_center_star = 2 → group 2
          - group 2, month 1: offset=11, cs=((2-1-11)%9)+1 = 9
        """
        target = date(2026, 1, 10)
        result = service.get_monthly_board(target_date=target)

        # stub solar_terms の 1月の star_number は ((1-1)%9)+1 = 1
        january_term_star_number = ((1 - 1) % 9) + 1

        # 年盤中宮星 経由の期待 center_star (stub: 2025→year_center_star=2→group 2)
        expected_center_star = 9

        # center_star が stub monthly_directions の期待値になっていること
        assert result.center_star == expected_center_star, (
            "center_star should resolve to 9 for 2026-01 (pre-立春, 2025→year_center_star=2→group 2); "
            "if this fails, group-based lookup around the year boundary may be incorrect"
        )
        # かつ、절기운성(star_number) をそのまま使っていないこと
        assert result.center_star != january_term_star_number, (
            "center_star must not equal the January solar_terms_data.star_number; "
            "if this fails, solar_terms_data.star_number may be used directly "
            "instead of resolving via solar_starts_data.star_number"
        )


class TestResolvePeriodStart:
    """resolve_period_start() の正常・異常ケースを検証する."""

    @pytest.fixture
    def service(self):
        return MonthlyBoardDomainService(
            solar_terms_repo=_make_solar_terms_repo(),
            solar_starts_repo=_make_solar_starts_repo(),
            star_grid_repo=_StubStarGridPatternRepo(),
            monthly_directions_repo=_make_monthly_directions_repo(),
        )

    @pytest.mark.parametrize("setsu_index", [1, 6, 12])
    def test_valid_setsu_index_returns_date(self, service, setsu_index):
        """유효 범위(1~12) 내 절월 인덱스는 date 를 반환한다."""
        result = service.resolve_period_start(2026, setsu_index)
        assert isinstance(result, date), (
            f"setsu_index={setsu_index} should return a date, got {result}"
        )

    @pytest.mark.parametrize("setsu_index", [0, 13, -1, 100])
    def test_invalid_setsu_index_raises_value_error(self, service, setsu_index):
        """유효 범위 밖 절월 인덱스는 ValueError 를 발생시킨다."""
        with pytest.raises(ValueError, match="setsu_index"):
            service.resolve_period_start(2026, setsu_index)

    def test_db_miss_returns_none(self, service):
        """DB에 해당 연도 절기 데이터가 없으면 None 을 반환한다."""
        # stub 에는 2030 데이터가 없음
        result = service.resolve_period_start(2030, 1)
        assert result is None

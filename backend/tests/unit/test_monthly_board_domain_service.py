"""월반(月盤) 기반 시스템 단위 테스트 (Phase 1 Foundation).

pytest 스타일을 따르며, 외부 DB/인프라 의존 없이 Stub 레포지토리를 사용한다.
설계서: docs/monthly-direction-with-powerstone.md 참조
"""
from __future__ import annotations

import pytest
from datetime import date

from core.utils.calendar_utils import (
    get_monthly_center_star,
    get_monthly_kanshi,
    get_year_stem_index_from_zodiac,
)
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
    """절기 데이터를 메모리에 보유하는 Stub ISolarTermsRepository."""

    def __init__(self, terms: list[_StubSolarTerm]):
        self._terms = terms

    def get_yearly_terms(self, year: int):
        return [t for t in self._terms if t.year == year]

    def get_term_by_month(self, year: int, month: int):
        for t in self._terms:
            if t.year == year and t.month == month:
                return t
        return None

    def get_term_by_date(self, target_date):
        for t in reversed(sorted(self._terms, key=lambda x: (x.year, x.month))):
            if t.solar_terms_date <= target_date:
                return t
        return None

    def get_spring_start(self, year: int):
        return next((t for t in self._terms if t.year == year and t.month == 1), None)

    def list_all(self):
        return self._terms

    def get_by_id(self, term_id: int):
        return None

    def update_term(self, *args, **kwargs):
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
# Tests — calendar_utils: get_monthly_center_star
# ══════════════════════════════════════════════════════

class TestGetMonthlyCenterStar:
    """月盤中宮星算出ロジックの検証 (設計書 §2-2 に基づく)."""

    # ── 上元グループ (1,4,7) → 1月(寅月) = 8 ──────────
    @pytest.mark.parametrize("year_star", [1, 4, 7])
    def test_upper_group_month1_is_8(self, year_star):
        assert get_monthly_center_star(year_star, 1) == 8

    # ── 中元グループ (2,5,8) → 1月(寅月) = 5 ──────────
    @pytest.mark.parametrize("year_star", [2, 5, 8])
    def test_mid_group_month1_is_5(self, year_star):
        assert get_monthly_center_star(year_star, 1) == 5

    # ── 下元グループ (3,6,9) → 1月(寅月) = 2 ──────────
    @pytest.mark.parametrize("year_star", [3, 6, 9])
    def test_low_group_month1_is_2(self, year_star):
        assert get_monthly_center_star(year_star, 1) == 2

    # ── 設計書 例示: 年盤中宮=4(上元) の全12ヶ月 ───────
    def test_upper_group_all_12_months_year_star_4(self):
        """設計書の例示 (年反中宮=4) と照合."""
        expected = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 9, 10: 8, 11: 7, 12: 6}
        for m, exp in expected.items():
            assert get_monthly_center_star(4, m) == exp, f"month={m} failed"

    # ── 1~9 範囲の循環検証 ─────────────────────────────
    def test_result_always_in_1_to_9(self):
        for year_star in range(1, 10):
            for month in range(1, 13):
                result = get_monthly_center_star(year_star, month)
                assert 1 <= result <= 9, f"out of range: year={year_star} month={month} result={result}"

    # ── 入力バリデーション ─────────────────────────────
    def test_invalid_year_center_star_raises(self):
        with pytest.raises(ValueError):
            get_monthly_center_star(0, 1)

    def test_invalid_setsu_month_index_raises(self):
        with pytest.raises(ValueError):
            get_monthly_center_star(5, 13)


# ══════════════════════════════════════════════════════
# Tests — calendar_utils: get_monthly_kanshi
# ══════════════════════════════════════════════════════

class TestGetMonthlyKanshi:
    """月干支算出ロジックの検証 (五虎遁 §3 に基づく)."""

    # ── 甲年(index=0) の1月(寅月) → 天干=丙 ───────────
    def test_kinen_month1_is_hinoto_tora(self):
        stem, branch = get_monthly_kanshi(0, 1)  # 甲年, 寅月
        assert stem == "丙"
        assert branch == "寅"

    # ── 乙年(index=1) の1月(寅月) → 天干=戊 ───────────
    def test_otunen_month1_is_tsuchinoe_tora(self):
        stem, branch = get_monthly_kanshi(1, 1)
        assert stem == "戊"
        assert branch == "寅"

    # ── 己年(index=5) は甲年と同じ丙から始まる ──────────
    def test_kinen_and_kinen_same_start(self):
        s0, b0 = get_monthly_kanshi(0, 1)
        s5, b5 = get_monthly_kanshi(5, 1)
        assert s0 == s5  # 甲=己 → 丙
        assert b0 == b5

    # ── 天干は10周期で循環する ───────────────────────────
    def test_stem_cycles_through_10(self):
        # 天干は10種なので, 月インデックス 1 と 11 は同じ天干になる
        stem_m1, _ = get_monthly_kanshi(0, 1)
        stem_m11, _ = get_monthly_kanshi(0, 11)
        assert stem_m1 == stem_m11, f"month=1 ({stem_m1}) should equal month=11 ({stem_m11})"

    # ── 地支は月インデックスに固定 ──────────────────────
    def test_branch_fixed_to_month_index(self):
        expected_branches = ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"]
        for m in range(1, 13):
            _, branch = get_monthly_kanshi(0, m)
            assert branch == expected_branches[m - 1], f"month={m}"

    # ── 入力バリデーション ─────────────────────────────
    def test_invalid_year_stem_raises(self):
        with pytest.raises(ValueError):
            get_monthly_kanshi(10, 1)

    def test_invalid_month_index_raises(self):
        with pytest.raises(ValueError):
            get_monthly_kanshi(0, 0)


# ══════════════════════════════════════════════════════
# Tests — calendar_utils: get_year_stem_index_from_zodiac
# ══════════════════════════════════════════════════════

class TestGetYearStemIndex:
    def test_koshi_is_0(self):
        assert get_year_stem_index_from_zodiac("甲子") == 0

    def test_otunouushi_is_1(self):
        assert get_year_stem_index_from_zodiac("乙丑") == 1

    def test_invalid_stem_raises(self):
        with pytest.raises(ValueError):
            get_year_stem_index_from_zodiac("X子")


# ══════════════════════════════════════════════════════
# Tests — MonthlyBoardDomainService
# ══════════════════════════════════════════════════════

def _make_solar_terms_repo() -> _StubSolarTermsRepo:
    """Year 2026 / 2025 stub 절기 데이터를 생성한다.

    setsu_month_index 1=寅月(立春) 부터 12=丑月(小寒) 순으로 절입일을 월 5일로 설정한다.
    (실제 절입일은 DB 에 따라 다르지만 로직 검증 목적의 픽스처)
    """
    terms = []
    for year in [2024, 2025, 2026, 2027]:
        for month in range(1, 13):
            # 简化: 각 절월을 해당 연도의 m번째 절월을 2월 4일부터 순서대로 배치
            import calendar
            # 절월 1=寅月: 2/4, 2=卯月: 3/6, ... 실제와 달라도 순서만 맞으면 된다
            day_of_year_offset = (month - 1) * 30
            from datetime import timedelta
            base = date(year, 2, 4) + timedelta(days=day_of_year_offset)
            # Adjust for dates exceeding December
            while base.year > year:
                base -= timedelta(days=1)

            zt = "甲子" if year == 2026 else "乙丑" if year == 2025 else "癸卯"
            terms.append(_StubSolarTerm(year, month, base, zodiac=zt, star_number=month))
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
            year_center_star=4,             # 上元グループ → 1月=8
            year_zodiac="甲子",
        )
        assert isinstance(result, MonthlyBoardResult)
        assert 1 <= result.center_star <= 9

    def test_grid_pattern_assembled(self, service):
        result = service.get_monthly_board(
            target_date=date(2026, 2, 5),
            year_center_star=4,
            year_zodiac="甲子",
        )
        assert result.grid_pattern is not None
        # Stub returns _StubGridPattern whose center_star equals result.center_star
        assert result.grid_pattern.center_star == result.center_star

    def test_month_zodiac_format(self, service):
        result = service.get_monthly_board(
            target_date=date(2026, 2, 5),
            year_center_star=4,
            year_zodiac="甲子",
        )
        assert len(result.month_zodiac) == 2
        assert result.month_zodiac[0] in "甲乙丙丁戊己庚辛壬癸"
        assert result.month_zodiac[1] in "子丑寅卯辰巳午未申酉戌亥"

    def test_period_start_before_period_end(self, service):
        result = service.get_monthly_board(
            target_date=date(2026, 2, 5),
            year_center_star=4,
            year_zodiac="甲子",
        )
        assert result.period_start <= result.period_end

    def test_invalid_year_zodiac_raises(self, service):
        with pytest.raises(ValueError):
            service.get_monthly_board(
                target_date=date(2026, 2, 5),
                year_center_star=4,
                year_zodiac="??",
            )

    def test_to_dict_has_required_keys(self, service):
        result = service.get_monthly_board(
            target_date=date(2026, 2, 5),
            year_center_star=4,
            year_zodiac="甲子",
        )
        d = result.to_dict()
        required_keys = {
            "setsu_month_index", "center_star", "month_stem", "month_branch",
            "month_zodiac", "period_start", "period_end", "grid_pattern",
        }
        assert required_keys.issubset(d.keys())

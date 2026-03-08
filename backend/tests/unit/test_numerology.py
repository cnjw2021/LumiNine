"""NumerologyService / NumerologyReadingRepository 단위 테스트.

커버리지:
  - Life Path Number 계산 정확성 (대표 생년월일 10+ 케이스)
  - 숫자 → 행성 매핑
  - NumerologyReadingRepository 9개 숫자 전체 로드
  - 다국어 키 존재 여부
  - 범위 밖 입력 에러 처리
"""
from __future__ import annotations

import pytest

from apps.fortunetelling.numerology.domain.services.numerology_service import NumerologyService
from apps.fortunetelling.numerology.domain.value_objects.numerology import (
    NumerologyNumber,
    NumerologyReading,
    Planet,
)
from apps.fortunetelling.numerology.infrastructure.persistence.numerology_reading_repository import (
    NumerologyReadingRepository,
)


# ══════════════════════════════════════════════════════
# NumerologyService — Life Path Number 계산
# ══════════════════════════════════════════════════════

class TestLifePathCalculation:
    @pytest.mark.parametrize("birth_date, expected_number", [
        # 1+9+8+4+0+7+0+9 = 38 → 3+8 = 11 (Master Number)
        ("1984-07-09", 11),
        # 1+9+6+7+0+6+0+5 = 34 → 3+4 = 7
        ("1967-06-05", 7),
        # 1+9+7+1+0+2+0+1 = 21 → 2+1 = 3
        ("1971-02-01", 3),
        # 1+9+7+2+0+1+0+1 = 21 → 2+1 = 3
        ("1972-01-01", 3),
        # 2+0+0+0+0+1+0+1 = 4
        ("2000-01-01", 4),
        # 1+9+9+9+1+2+3+1 = 35 → 3+5 = 8
        ("1999-12-31", 8),
        # 1+9+9+0+0+9+0+9 = 37 → 3+7 = 10 → 1+0 = 1
        ("1990-09-09", 1),
        # 2+0+2+5+0+3+1+5 = 18 → 1+8 = 9
        ("2025-03-15", 9),
        # 1+9+8+8+0+8+0+8 = 42 → 4+2 = 6
        ("1988-08-08", 6),
        # 1+9+9+5+0+5+0+5 = 34 → 3+4 = 7
        ("1995-05-05", 7),
    ])
    def test_life_path_number(self, birth_date: str, expected_number: int):
        result = NumerologyService.calculate_life_path_number(birth_date)
        assert result.number == expected_number

    def test_returns_numerology_number(self):
        result = NumerologyService.calculate_life_path_number("1984-07-09")
        assert isinstance(result, NumerologyNumber)

    def test_planet_mapping(self):
        """각 숫자에 올바른 행성이 매핑되어야 한다."""
        result = NumerologyService.calculate_life_path_number("1984-07-09")
        # 1984-07-09 → 11 (Master Number) → Neptune (전용 행성)
        assert result.planet == Planet.NEPTUNE

    def test_datetime_format_with_time(self):
        """'YYYY-MM-DD HH:MM' 형식도 지원해야 한다."""
        result = NumerologyService.calculate_life_path_number("1984-07-09 15:30")
        assert result.number == 11  # Master Number

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            NumerologyService.calculate_life_path_number("invalid")

    def test_all_numbers_1_to_9_reachable(self):
        """1~9 모든 숫자가 나올 수 있는지 확인."""
        # 각 숫자별 검증된 생년월일 → 기대 Life Path Number
        test_dates = [
            ("1990-09-09", 1),  # 1+9+9+0+0+9+0+9=37 → 10 → 1
            ("1980-01-01", 2),  # 1+9+8+0+0+1+0+1=20 → 2+0=2
            ("1971-02-01", 3),  # 1+9+7+1+0+2+0+1=21 → 3
            ("2000-01-01", 4),  # 2+0+0+0+0+1+0+1=4
            ("2000-01-02", 5),  # 2+0+0+0+0+1+0+2=5
            ("1988-08-08", 6),  # 1+9+8+8+0+8+0+8=42 → 6
            ("1967-06-05", 7),  # 1+9+6+7+0+6+0+5=34 → 7
            ("1999-12-31", 8),  # 1+9+9+9+1+2+3+1=35 → 8
            ("2025-03-15", 9),  # 2+0+2+5+0+3+1+5=18 → 9
        ]
        seen = set()
        for date, expected in test_dates:
            r = NumerologyService.calculate_life_path_number(date)
            assert r.number == expected, f"{date} → {r.number} (expected {expected})"
            seen.add(r.number)

        assert seen == set(range(1, 10)), f"커버되지 않은 숫자: {set(range(1,10)) - seen}"


# ══════════════════════════════════════════════════════
# NumerologyService — Personal Year Number 계산
# ══════════════════════════════════════════════════════

class TestPersonalYearCalculation:
    @pytest.mark.parametrize("birth_date, target_year, expected_number", [
        # 2+0+2+6+0+7+0+9 = 26 → 2+6 = 8
        ("1984-07-09", 2026, 8),
        # 2+0+2+5+0+7+0+9 = 25 → 2+5 = 7
        ("1984-07-09", 2025, 7),
        # 2+0+2+6+0+1+0+1 = 12 → 1+2 = 3
        ("2000-01-01", 2026, 3),
        # 2+0+2+6+1+2+3+1 = 17 → 1+7 = 8
        ("1999-12-31", 2026, 8),
        # 2+0+2+6+0+9+0+9 = 28 → 2+8 = 10 → 1+0 = 1
        ("1990-09-09", 2026, 1),
    ])
    def test_personal_year_number(self, birth_date: str, target_year: int, expected_number: int):
        result = NumerologyService.calculate_personal_year_number(birth_date, target_year)
        assert result.number == expected_number

    def test_returns_numerology_number(self):
        result = NumerologyService.calculate_personal_year_number("1984-07-09", 2026)
        assert isinstance(result, NumerologyNumber)

    def test_planet_mapping(self):
        result = NumerologyService.calculate_personal_year_number("1984-07-09", 2026)
        # Personal Year 8 → Saturn
        assert result.planet == Planet.SATURN

    def test_datetime_format_with_time(self):
        result = NumerologyService.calculate_personal_year_number("1984-07-09 15:30", 2026)
        assert result.number == 8

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            NumerologyService.calculate_personal_year_number("invalid", 2026)

    def test_different_years_different_results(self):
        """연도가 달라지면 Personal Year Number도 달라져야 한다."""
        results = set()
        for year in range(2020, 2030):
            r = NumerologyService.calculate_personal_year_number("1984-07-09", year)
            results.add(r.number)
        # 10년간 최소 5개 이상의 서로 다른 숫자가 나와야 함 (중복 허용)
        assert len(results) >= 5


class TestReduceWithMaster:
    @pytest.mark.parametrize("n, expected", [
        (1, 1), (9, 9), (10, 1),
        (11, 11),  # Master Number 유지
        (22, 22),  # Master Number 유지
        (33, 33),  # Master Number 유지
        (38, 11),  # 3+8=11 → Master Number
        (100, 1),
        (44, 8),   # 4+4=8 → 일반 축소
    ])
    def test_reduction(self, n: int, expected: int):
        assert NumerologyService._reduce_with_master(n) == expected


class TestPlanetNameLocale:
    def test_japanese(self):
        num = NumerologyNumber(number=1, planet=Planet.SUN)
        assert num.get_planet_name("ja") == "太陽"

    def test_korean(self):
        num = NumerologyNumber(number=2, planet=Planet.MOON)
        assert num.get_planet_name("ko") == "달"

    def test_english(self):
        num = NumerologyNumber(number=3, planet=Planet.JUPITER)
        assert num.get_planet_name("en") == "Jupiter"


# ══════════════════════════════════════════════════════
# NumerologyReadingRepository
# ══════════════════════════════════════════════════════

@pytest.fixture
def repo() -> NumerologyReadingRepository:
    return NumerologyReadingRepository()


class TestNumerologyReadingRepository:
    def test_all_nine_numbers_loaded(self, repo: NumerologyReadingRepository):
        """1~9 모든 숫자의 데이터가 로드되어야 한다."""
        for n in range(1, 10):
            reading = repo.get_reading(n, "ja")
            assert reading.number == n

    def test_reading_returns_correct_type(self, repo: NumerologyReadingRepository):
        reading = repo.get_reading(1, "ja")
        assert isinstance(reading, NumerologyReading)

    def test_reading_has_keywords(self, repo: NumerologyReadingRepository):
        for n in range(1, 10):
            reading = repo.get_reading(n, "ja")
            assert len(reading.keywords) >= 3

    def test_reading_has_description(self, repo: NumerologyReadingRepository):
        for n in range(1, 10):
            reading = repo.get_reading(n, "ja")
            assert len(reading.description) > 0

    def test_reading_planet_matches(self, repo: NumerologyReadingRepository):
        reading = repo.get_reading(1, "ja")
        assert reading.planet == Planet.SUN

    @pytest.mark.parametrize("locale", ["ja", "ko", "en"])
    def test_locale_support(self, repo: NumerologyReadingRepository, locale: str):
        """ja, ko, en 모든 로캘에서 데이터가 반환되어야 한다."""
        for n in range(1, 10):
            reading = repo.get_reading(n, locale)
            assert len(reading.keywords) >= 3
            assert len(reading.description) > 0

    @pytest.mark.parametrize("invalid_number", [0, 10, -1, 100])
    def test_invalid_number_raises(self, repo: NumerologyReadingRepository, invalid_number: int):
        with pytest.raises(ValueError):
            repo.get_reading(invalid_number, "ja")

    def test_strengths_and_weaknesses(self, repo: NumerologyReadingRepository):
        for n in range(1, 10):
            reading = repo.get_reading(n, "ja")
            assert len(reading.strengths) >= 2
            assert len(reading.weaknesses) >= 1

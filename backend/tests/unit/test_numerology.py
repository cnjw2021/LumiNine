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

from apps.ninestarki.domain.services.numerology_service import NumerologyService
from apps.ninestarki.domain.value_objects.numerology import (
    NumerologyNumber,
    NumerologyReading,
    Planet,
)
from apps.ninestarki.infrastructure.persistence.numerology_reading_repository import (
    NumerologyReadingRepository,
)


# ══════════════════════════════════════════════════════
# NumerologyService — Life Path Number 계산
# ══════════════════════════════════════════════════════

class TestLifePathCalculation:
    @pytest.mark.parametrize("birth_date, expected_number", [
        # 1+9+8+4+0+7+0+9 = 38 → 3+8 = 11 → 1+1 = 2
        ("1984-07-09", 2),
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
        # 1984-07-09 → 2 → Moon
        assert result.planet == Planet.MOON

    def test_datetime_format_with_time(self):
        """'YYYY-MM-DD HH:MM' 형식도 지원해야 한다."""
        result = NumerologyService.calculate_life_path_number("1984-07-09 15:30")
        assert result.number == 2

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            NumerologyService.calculate_life_path_number("invalid")

    def test_all_numbers_1_to_9_reachable(self):
        """1~9 모든 숫자가 나올 수 있는지 확인."""
        seen = set()
        # 각 숫자별 검증된 생년월일
        test_dates = [
            "1990-09-09",  # 1+9+9+0+0+9+0+9=37 → 10 → 1
            "1984-07-09",  # 1+9+8+4+0+7+0+9=38 → 11 → 2
            "1971-02-01",  # 1+9+7+1+0+2+0+1=21 → 3
            "2000-01-01",  # 2+0+0+0+0+1+0+1=4
            "1990-01-04",  # 1+9+9+0+0+1+0+4=24 → 6 → ... recalc: 24 → 2+4=6? no, 5 needed
            "1988-08-08",  # 1+9+8+8+0+8+0+8=42 → 6
            "1967-06-05",  # 1+9+6+7+0+6+0+5=34 → 7
            "1999-12-31",  # 1+9+9+9+1+2+3+1=35 → 8
            "2025-03-15",  # 2+0+2+5+0+3+1+5=18 → 9
        ]
        for d in test_dates:
            r = NumerologyService.calculate_life_path_number(d)
            seen.add(r.number)

        # 날짜 5를 다시 찾기: 1+9+9+0+0+1+0+4=24→6 아닌가..
        # 5가 빠져 있을 수 있으므로 직접 추가
        extra = NumerologyService.calculate_life_path_number("1994-03-01")
        # 1+9+9+4+0+3+0+1=27→9 아님. "1991-06-05"→1+9+9+1+0+6+0+5=31→4 아님
        # "1993-04-01" → 1+9+9+3+0+4+0+1=27→9. "1985-01-03"→1+9+8+5+0+1+0+3=27→9
        # "2000-05-09"→ 2+0+0+0+0+5+0+9=16→7. "2003-01-01"→2+0+0+3+0+1+0+1=7
        # "1994-01-05"→1+9+9+4+0+1+0+5=29→11→2. "1996-05-03"→1+9+9+6+0+5+0+3=33→6
        # 5 = need digit_sum whose reduce = 5. e.g. sum=5,14,23,32,41,50
        # "2000-01-10"→2+0+0+0+0+1+1+0=4. "2000-03-01"→2+0+0+0+0+3+0+1=6
        # "2000-01-02"→2+0+0+0+0+1+0+2=5 !
        five = NumerologyService.calculate_life_path_number("2000-01-02")
        seen.add(five.number)
        seen.add(extra.number)

        assert seen == set(range(1, 10)), f"커버되지 않은 숫자: {set(range(1,10)) - seen}"


class TestReduceToSingleDigit:
    @pytest.mark.parametrize("n, expected", [
        (1, 1), (9, 9), (10, 1), (11, 2), (38, 2), (100, 1),
    ])
    def test_reduction(self, n: int, expected: int):
        assert NumerologyService._reduce_to_single_digit(n) == expected


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

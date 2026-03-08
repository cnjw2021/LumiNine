"""NumerologyService — 수비술 Life Path Number 계산.

생년월일의 각 자릿수를 합산하여 한 자릿수(1~9) 또는 Master Number(11/22/33)
로 축소하는 순수 비즈니스 로직.  StarCalculatorService 와 동일한 static-method 패턴.
"""
from __future__ import annotations

from apps.reading.numerology.domain.value_objects.numerology import (
    MASTER_NUMBERS,
    NumerologyNumber,
    NUMBER_TO_PLANET,
)


class NumerologyService:
    """수비술 계산 순수 비즈니스 로직."""

    @staticmethod
    def _reduce_with_master(n: int) -> int:
        """양의 정수를 한 자릿수(1~9) 또는 Master Number(11/22/33)로 축소.

        예: 38 → 3+8=11 → Master Number이므로 11 유지
            39 → 3+9=12 → 1+2=3
        """
        while n > 9:
            if n in MASTER_NUMBERS:
                return n
            n = sum(int(d) for d in str(n))
        return n

    @staticmethod
    def calculate_life_path_number(birth_date: str) -> NumerologyNumber:
        """생년월일 문자열 → Life Path Number 계산.

        Args:
            birth_date: ``"YYYY-MM-DD"`` 또는 ``"YYYY-MM-DD HH:MM"`` 형식의 생년월일
                (시간 정보가 포함된 경우 시간 부분은 무시됨)

        Returns:
            NumerologyNumber  (1~9 또는 11/22/33 + 대응 행성)

        Raises:
            ValueError: 날짜 형식이 올바르지 않은 경우
        """
        # "YYYY-MM-DD" 또는 "YYYY-MM-DD HH:MM" 둘 다 대응
        date_part = birth_date.strip().split(" ")[0]
        parts = date_part.split("-")
        if len(parts) != 3:
            raise ValueError(
                f"생년월일 형식이 올바르지 않습니다: {birth_date} (YYYY-MM-DD 필요)"
            )

        year, month, day = parts
        digits = year + month + day

        # 모든 문자가 숫자이며 최소 한 자릿수 이상인지 확인
        if not digits or not digits.isdigit():
            raise ValueError(
                f"생년월일 형식이 올바르지 않습니다: {birth_date} (숫자 YYYY-MM-DD 필요)"
            )

        digit_sum = sum(int(d) for d in digits)
        life_path = NumerologyService._reduce_with_master(digit_sum)

        # Life Path Number 가 1~9 범위(매핑에 존재)인지 확인
        if life_path not in NUMBER_TO_PLANET:
            raise ValueError(
                f"유효하지 않은 Life Path Number가 계산되었습니다: {life_path}"
            )

        planet = NUMBER_TO_PLANET[life_path]
        return NumerologyNumber(number=life_path, planet=planet)

    @staticmethod
    def calculate_personal_year_number(birth_date: str, target_year: int) -> NumerologyNumber:
        """생년월일 + 대상 연도 → Personal Year Number 계산.

        Personal Year Number = (생월 + 생일 + 대상 연도) 의 각 자릿수를
        합산하여 한 자릿수(1~9)로 축소한 값.

        Args:
            birth_date: ``"YYYY-MM-DD"`` 또는 ``"YYYY-MM-DD HH:MM"`` 형식의 생년월일
            target_year: 대상 연도 (예: 2026)

        Returns:
            NumerologyNumber  (1~9 또는 11/22/33 + 대응 행성)

        Raises:
            ValueError: 날짜 형식이 올바르지 않은 경우
        """
        if not isinstance(target_year, int) or not 1 <= target_year <= 9999:
            raise ValueError(
                f"target_year 는 1~9999 범위의 정수여야 합니다: {target_year}"
            )

        date_part = birth_date.strip().split(" ")[0]
        parts = date_part.split("-")
        if len(parts) != 3:
            raise ValueError(
                f"생년월일 형식이 올바르지 않습니다: {birth_date} (YYYY-MM-DD 필요)"
            )

        year_str, month, day = parts

        if not (year_str.isdigit() and month.isdigit() and day.isdigit()):
            raise ValueError(
                f"생년월일 형식이 올바르지 않습니다: {birth_date} (숫자 YYYY-MM-DD 필요)"
            )

        # target_year + month + day 의 전체 자릿수를 합산
        digits = str(target_year) + month + day
        digit_sum = sum(int(d) for d in digits)
        personal_year = NumerologyService._reduce_with_master(digit_sum)

        if personal_year not in NUMBER_TO_PLANET:
            raise ValueError(
                f"유효하지 않은 Personal Year Number가 계산되었습니다: {personal_year}"
            )

        planet = NUMBER_TO_PLANET[personal_year]
        return NumerologyNumber(number=personal_year, planet=planet)

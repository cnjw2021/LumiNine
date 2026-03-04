"""NumerologyService — 수비술 Life Path Number 계산.

생년월일의 각 자릿수를 합산하여 한 자릿수(1~9)가 될 때까지 축소하는
순수 비즈니스 로직.  StarCalculatorService 와 동일한 static-method 패턴.
"""
from __future__ import annotations

from apps.ninestarki.domain.value_objects.numerology import (
    NumerologyNumber,
    NUMBER_TO_PLANET,
)


class NumerologyService:
    """수비술 계산 순수 비즈니스 로직."""

    @staticmethod
    def _reduce_to_single_digit(n: int) -> int:
        """양의 정수를 한 자릿수(1~9)로 축소.

        예: 38 → 3+8=11 → 1+1=2
        """
        while n > 9:
            n = sum(int(d) for d in str(n))
        return n

    @staticmethod
    def calculate_life_path_number(birth_date: str) -> NumerologyNumber:
        """생년월일 문자열 → Life Path Number 계산.

        Args:
            birth_date: ``"YYYY-MM-DD"`` 형식의 생년월일

        Returns:
            NumerologyNumber  (1~9 + 대응 행성)

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
        life_path = NumerologyService._reduce_to_single_digit(digit_sum)

        # Life Path Number 가 1~9 범위(매핑에 존재)인지 확인
        if life_path not in NUMBER_TO_PLANET:
            raise ValueError(
                f"유효하지 않은 Life Path Number가 계산되었습니다: {life_path}"
            )

        planet = NUMBER_TO_PLANET[life_path]
        return NumerologyNumber(number=life_path, planet=planet)

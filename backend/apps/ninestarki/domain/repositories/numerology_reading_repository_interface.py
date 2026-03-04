"""INumerologyReadingRepository — 수비술 숫자 특성 데이터 리포지토리 인터페이스."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from apps.ninestarki.domain.value_objects.numerology import NumerologyReading


class INumerologyReadingRepository(ABC):
    """수비술 숫자별 특성 데이터를 제공하는 리포지토리 인터페이스."""

    @abstractmethod
    def get_reading(self, number: int, locale: str = "ja") -> NumerologyReading:
        """수비술 숫자(1~9)의 특성 데이터 반환.

        Args:
            number: Life Path Number (1~9)
            locale: 언어 코드 (ja, ko, en)

        Returns:
            해당 숫자의 NumerologyReading

        Raises:
            ValueError: 숫자가 1~9 범위를 벗어난 경우
        """

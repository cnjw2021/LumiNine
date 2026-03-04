"""NumerologyReadingRepository — JSON 기반 수비술 특성 데이터 리포지토리.

PowerStoneRepository 패턴을 따라 JSON 파일에서 데이터를 로드합니다.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from apps.ninestarki.domain.repositories.numerology_reading_repository_interface import (
    INumerologyReadingRepository,
)
from apps.ninestarki.domain.value_objects.numerology import (
    NumerologyReading,
    NUMBER_TO_PLANET,
)

_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "numerology_readings.json"


class NumerologyReadingRepository(INumerologyReadingRepository):
    """JSON 파일 기반 수비술 특성 데이터 리포지토리."""

    def __init__(self) -> None:
        with open(_DATA_PATH, encoding="utf-8") as f:
            self._raw: Dict[str, Any] = json.load(f)

    def get_reading(self, number: int, locale: str = "ja") -> NumerologyReading:
        """수비술 숫자(1~9)의 특성 데이터 반환."""
        if number < 1 or number > 9:
            raise ValueError(
                f"유효하지 않은 수비술 숫자입니다: {number} (1~9 범위)"
            )

        key = str(number)
        data = self._raw.get(key)
        if data is None:
            raise ValueError(
                f"수비술 숫자 {number} 의 데이터를 찾을 수 없습니다."
            )

        planet = NUMBER_TO_PLANET[number]
        return NumerologyReading(
            number=number,
            planet=planet,
            keywords=data["keywords"].get(locale, data["keywords"].get("ja", [])),
            description=data["description"].get(locale, data["description"].get("ja", "")),
            strengths=data["strengths"].get(locale, data["strengths"].get("ja", [])),
            weaknesses=data["weaknesses"].get(locale, data["weaknesses"].get("ja", [])),
        )

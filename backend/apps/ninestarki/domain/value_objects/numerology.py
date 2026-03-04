"""수비술(数秘術) Value Objects.

Life Path Number 계산 결과 및 행성 매핑을 위한 데이터 클래스.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class Planet(Enum):
    """수비술 숫자에 대응하는 행성."""
    SUN = "sun"
    MOON = "moon"
    JUPITER = "jupiter"
    RAHU = "rahu"
    MERCURY = "mercury"
    VENUS = "venus"
    KETU = "ketu"
    SATURN = "saturn"
    MARS = "mars"


# ── 숫자 → 행성 매핑 ────────────────────────────────
NUMBER_TO_PLANET: Dict[int, Planet] = {
    1: Planet.SUN,
    2: Planet.MOON,
    3: Planet.JUPITER,
    4: Planet.RAHU,
    5: Planet.MERCURY,
    6: Planet.VENUS,
    7: Planet.KETU,
    8: Planet.SATURN,
    9: Planet.MARS,
}

# ── 행성 이름 다국어 ────────────────────────────────
PLANET_NAMES: Dict[Planet, Dict[str, str]] = {
    Planet.SUN:     {"ja": "太陽", "ko": "태양", "en": "Sun"},
    Planet.MOON:    {"ja": "月",   "ko": "달",   "en": "Moon"},
    Planet.JUPITER: {"ja": "木星", "ko": "목성", "en": "Jupiter"},
    Planet.RAHU:    {"ja": "ラーフ", "ko": "라후", "en": "Rahu"},
    Planet.MERCURY: {"ja": "水星", "ko": "수성", "en": "Mercury"},
    Planet.VENUS:   {"ja": "金星", "ko": "금성", "en": "Venus"},
    Planet.KETU:    {"ja": "ケートゥ", "ko": "켓투", "en": "Ketu"},
    Planet.SATURN:  {"ja": "土星", "ko": "토성", "en": "Saturn"},
    Planet.MARS:    {"ja": "火星", "ko": "화성", "en": "Mars"},
}


@dataclass(frozen=True)
class NumerologyNumber:
    """수비술 Life Path Number + 행성 정보."""
    number: int
    planet: Planet

    def get_planet_name(self, locale: str = "ja") -> str:
        """행성 이름의 로캘별 표시 문자열 반환."""
        names = PLANET_NAMES.get(self.planet, {})
        return names.get(locale) or names.get("ja") or self.planet.value


@dataclass(frozen=True)
class NumerologyReading:
    """수비술 숫자별 특성 읽기 데이터."""
    number: int
    planet: Planet
    keywords: List[str]
    description: str
    strengths: List[str]
    weaknesses: List[str]

"""수비술(数秘術) Value Objects.

Life Path Number 계산 결과 및 행성 매핑을 위한 데이터 클래스.
Master Number(11, 22, 33)를 포함한 확장 매핑을 제공한다.
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


# ── Master Number 상수 ───────────────────────────────
MASTER_NUMBERS: frozenset = frozenset({11, 22, 33})

# Master Number → base number (파워스톤 매핑용)
MASTER_TO_BASE: Dict[int, int] = {11: 2, 22: 4, 33: 6}

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
    # Master Numbers (base number 와 동일 행성)
    11: Planet.MOON,     # 11 → 2 → Moon
    22: Planet.RAHU,     # 22 → 4 → Rahu
    33: Planet.VENUS,    # 33 → 6 → Venus
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

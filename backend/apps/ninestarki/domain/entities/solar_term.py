from __future__ import annotations
from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True)
class SolarTerm:
    year: int
    month: int
    solar_terms_date: date
    solar_terms_time: time | None
    solar_terms_name: str
    zodiac: str
    star_number: int



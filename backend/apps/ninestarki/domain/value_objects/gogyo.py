"""오행(五行) 및 오행 관계 Enum.

오행: 木(목)·火(화)·土(토)·金(금)·水(수)
관계: 相生(상생)·相剋(상극)·比和(비화)
"""
from __future__ import annotations

from enum import Enum


class Gogyo(str, Enum):
    """오행(五行) — 목·화·토·금·수."""

    WOOD = "木"
    FIRE = "火"
    EARTH = "土"
    METAL = "金"
    WATER = "水"


class GogyoRelation(str, Enum):
    """오행 간 관계."""

    SOJO = "相生"    # 서로 도움 (생하는 관계)
    SOKOKU = "相剋"  # 서로 억제 (극하는 관계)
    HIWA = "比和"    # 같은 오행

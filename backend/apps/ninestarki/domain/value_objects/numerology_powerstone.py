"""수비술 기반 파워스톤 Value Objects.

- NumerologyStone: 단일 스톤 정보 (다국어 이름 + 설명)
- NumerologyStoneRecommendation: 레이어별 추천 결과 (주석 + 부석)
- NumerologyPowerStoneResult: 4-Layer 최종 결과
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class NumerologyStone:
    """수비술 파워스톤 정보 (불변).

    gogyo 기반 PowerStone 과 달리 행성-에너지 기반이므로
    gogyo/is_primary 필드를 갖지 않는다.

    Note:
        ``frozen=True`` 이지만 ``names``/``description`` 은 dict 이므로
        내부 mutation 은 차단되지 않는다. 호출측에서 dict 값을
        변경하지 않도록 주의해야 한다.
    """

    id: str                          # "ruby", "moonstone" 등 고유 식별자
    names: Dict[str, str]            # {"ja": "ルビー", "ko": "루비", "en": "Ruby"}
    description: Dict[str, str]      # locale별 설명

    def __post_init__(self) -> None:
        if not self.names:
            raise ValueError("NumerologyStone.names 는 최소 1개의 locale 이름을 포함해야 합니다.")
        if not self.description:
            raise ValueError("NumerologyStone.description 은 최소 1개의 locale 설명을 포함해야 합니다.")

    def get_name(self, locale: str = "ja") -> str:
        """지정 locale의 이름 반환. fallback: locale → ja → 첫 번째 값."""
        return self.names.get(locale) or self.names.get("ja") or next(iter(self.names.values()))

    def get_description(self, locale: str = "ja") -> str:
        """지정 locale의 설명 반환. fallback: locale → ja → 첫 번째 값."""
        return self.description.get(locale) or self.description.get("ja") or next(iter(self.description.values()))


@dataclass(frozen=True)
class NumerologyStoneRecommendation:
    """수비술 단일 레이어 추천 결과."""

    layer: str                       # "overall" | "health" | "wealth" | "love"
    primary: NumerologyStone         # 주석
    secondary: NumerologyStone       # 부석
    planet: str                      # 지배 행성 ("sun", "moon", ...)


@dataclass(frozen=True)
class NumerologyPowerStoneResult:
    """수비술 기반 4-Layer 파워스톤 추천 최종 결과."""

    life_path_number: int
    planet: str
    overall: NumerologyStoneRecommendation      # 전체운
    health: NumerologyStoneRecommendation        # 건강운
    wealth: NumerologyStoneRecommendation        # 재물운
    love: NumerologyStoneRecommendation          # 연애운

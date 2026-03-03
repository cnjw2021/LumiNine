"""파워스톤 관련 Value Objects (Frozen Dataclass).

- PowerStone: 단일 스톤 정보 (다국어 이름 지원)
- StoneRecommendation: 레이어별 추천 결과
- PowerStoneResult: 3-Layer 최종 결과
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from apps.ninestarki.domain.value_objects.gogyo import Gogyo


@dataclass(frozen=True)
class PowerStone:
    """단일 파워스톤 정보 (불변). 이름은 locale별로 보유."""

    id: str                         # "emerald", "garnet" 등 고유 식별자
    names: Dict[str, str]           # {"ja": "エメラルド", "ko": "에메랄드", "en": "Emerald"}
    gogyo: Gogyo                    # 대응 오행
    is_primary: bool                # 해당 오행의 주석 여부

    def get_name(self, locale: str = "ja") -> str:
        """지정 locale의 이름 반환. fallback: locale → ja → 첫 번째 값."""
        return self.names.get(locale) or self.names.get("ja") or next(iter(self.names.values()))


@dataclass(frozen=True)
class StoneRecommendation:
    """단일 레이어의 추천 결과. reason_key 를 통해 다국어 사유 지원."""

    stone: PowerStone
    layer: str                                          # "base" | "monthly" | "protection"
    gogyo: Gogyo                                        # 매칭에 사용된 오행
    reason_key: str                                     # 메시지 카탈로그 키
    reason_params: Dict[str, str] = field(default_factory=dict)
    direction: Optional[str] = None                     # 관련 방위 (L2/L3)
    threat_mark: Optional[str] = None                   # 관련 흉살 (L3)


@dataclass(frozen=True)
class PowerStoneResult:
    """3-Layer 파워스톤 추천 최종 결과."""

    base_stone: StoneRecommendation       # L1 기본석
    monthly_stone: StoneRecommendation    # L2 월운석
    protection_stone: StoneRecommendation  # L3 호신석

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
    """단일 파워스톤 정보 (불변). 이름은 locale별로 보유.

    Note:
        frozen=True 이지만, names (Dict) 자체는 mutable 하다.
        완전한 불변성이 필요하면 MappingProxyType 등으로 래핑할 수 있으나,
        현 단계에서는 도메인 내부에서만 생성·소비하므로 frozen 으로 충분하다.
    """

    id: str                         # "emerald", "garnet" 등 고유 식별자
    names: Dict[str, str]           # {"ja": "エメラルド", "ko": "에메랄드", "en": "Emerald"}
    gogyo: Gogyo                    # 대응 오행
    is_primary: bool                # 해당 오행의 주석 여부

    def __post_init__(self) -> None:
        if not self.names:
            raise ValueError("PowerStone.names 는 최소 1개의 locale 이름을 포함해야 합니다.")

    def get_name(self, locale: str = "ja") -> str:
        """지정 locale의 이름 반환. fallback: locale → ja → 첫 번째 값."""
        return self.names.get(locale) or self.names.get("ja") or next(iter(self.names.values()))


@dataclass(frozen=True)
class StoneRecommendation:
    """단일 레이어의 추천 결과. reason_key 를 통해 다국어 사유 지원.

    Note:
        frozen=True 이지만, reason_params (Dict) 자체는 mutable 하다.
        PowerStone.names 와 동일한 한계이며, 현 단계에서는 도메인 내부
        생성·소비 패턴이므로 frozen 으로 충분하다.
    """

    stone: PowerStone
    layer: str                                          # "base" | "monthly" | "protection"
    gogyo: Gogyo                                        # 매칭에 사용된 오행
    reason_key: str                                     # 메시지 카탈로그 키
    reason_params: Dict[str, str] = field(default_factory=dict)
    direction: Optional[str] = None                     # 관련 방위 (L2/L3)
    threat_mark: Optional[str] = None                   # 관련 흉살 (L3)


@dataclass(frozen=True)
class PowerStoneResult:
    """3-Layer 파워스톤 추천 최종 결과.

    Note:
        길방위가 없는 경우 ``monthly_stone`` 은 ``None`` 이 된다.
        Layer 3 (호신석) 은 흉살 방위에서 결정하므로 항상 존재한다.
    """

    base_stone: StoneRecommendation                   # L1 기본석
    monthly_stone: Optional[StoneRecommendation]      # L2 월운석 (길방위 없으면 None)
    protection_stone: StoneRecommendation              # L3 호신석

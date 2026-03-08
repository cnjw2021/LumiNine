"""IPowerStoneMatchingEngine — 파워스톤 매칭 엔진 인터페이스.

3-Layer 추천 로직의 퍼사드 인터페이스.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from apps.reading.powerstone.domain.value_objects.powerstone import PowerStoneResult


class IPowerStoneMatchingEngine(ABC):
    """파워스톤 3-Layer 매칭 엔진 인터페이스.

    Layer 1: 기본석 (본명성 → 오행 → 기본석)
    Layer 2: 월운석 (최적 길방위 → 오행 → 월운석)
    Layer 3: 호신석 (최악 흉살 → 상극 오행 → 호신석)
    """

    @abstractmethod
    def recommend(
        self,
        main_star: int,
        directions: Dict[str, Any],
    ) -> PowerStoneResult:
        """3-Layer 추천 실행 (퍼사드 메서드).

        Args:
            main_star: 본명성 번호 (1~9)
            directions: MonthlyDirections 결과 (방위별 길흉 판정)

        Returns:
            기본석·월운석·호신석으로 구성된 PowerStoneResult.
            길방위가 없으면 ``monthly_stone`` 은 ``None`` 이 된다.

        Raises:
            PowerStoneMatchingError: 매칭 과정에서 오류 발생한 경우
        """

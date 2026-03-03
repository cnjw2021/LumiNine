"""GogyoService 도메인 포트 인터페이스.

오행(五行) 판별·상극 유틸리티의 추상 계약.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from apps.ninestarki.domain.value_objects.gogyo import Gogyo, GogyoRelation


class IGogyoService(ABC):
    """오행(五行) 서비스의 도메인 포트.

    순수 비즈니스 로직만 담당하며, 외부 I/O 가 없다.
    런타임 DI(Injector)는 ABC 기반 바인딩을 사용하므로,
    프로젝트 표준(ABC + @abstractmethod)에 맞춰 정의한다.
    """

    @abstractmethod
    def star_to_gogyo(self, star_number: int) -> Gogyo:
        """본명성 번호(1~9) → 대응 오행 변환.

        Args:
            star_number: 본명성 번호 (1~9)

        Returns:
            대응 오행(Gogyo)

        Raises:
            PowerStoneMatchingError: 유효하지 않은 star_number
        """

    @abstractmethod
    def direction_to_gogyo(self, direction: str) -> Gogyo:
        """방위 문자열 → 대응 오행 변환.

        Args:
            direction: 방위 문자열 ("north", "south", "east", ...)

        Returns:
            대응 오행(Gogyo)

        Raises:
            PowerStoneMatchingError: 알 수 없는 direction
        """

    @abstractmethod
    def get_relation(self, a: Gogyo, b: Gogyo) -> GogyoRelation:
        """두 오행 간 관계(상생/상극/비화) 판별.

        Args:
            a: 첫 번째 오행
            b: 두 번째 오행

        Returns:
            GogyoRelation (SOJO / SOKOKU / HIWA)
        """

    @abstractmethod
    def get_counter_gogyo(self, target: Gogyo) -> Gogyo:
        """주어진 오행을 극하는(억제하는) 오행 반환.

        Args:
            target: 억제 대상 오행

        Returns:
            target 을 극하는 오행
        """

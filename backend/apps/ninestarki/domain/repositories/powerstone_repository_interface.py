"""IPowerStoneRepository — 파워스톤 데이터 접근 인터페이스.

기존 domain/repositories/ 컨벤션 위치에 배치.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from apps.ninestarki.domain.value_objects.gogyo import Gogyo
from apps.ninestarki.domain.value_objects.powerstone import PowerStone


class IPowerStoneRepository(ABC):
    """파워스톤 데이터 접근 도메인 포트.

    구현체는 Infrastructure 레이어(PowerStoneRepository)에 위치하며,
    JSON 기반 정적 데이터를 로드한다.
    """

    @abstractmethod
    def get_primary_by_gogyo(self, gogyo: Gogyo) -> PowerStone:
        """지정 오행의 주석(is_primary=True) 반환.

        Args:
            gogyo: 조회할 오행

        Returns:
            해당 오행의 주석 PowerStone
        """

    @abstractmethod
    def get_secondaries_by_gogyo(self, gogyo: Gogyo) -> List[PowerStone]:
        """지정 오행의 부석(is_primary=False) 목록 반환.

        Args:
            gogyo: 조회할 오행

        Returns:
            부석 PowerStone 리스트
        """

    @abstractmethod
    def get_base_stone_for_star(self, star_number: int) -> PowerStone:
        """본명성 번호(1~9) → 기본석 반환.

        Args:
            star_number: 본명성 번호 (1~9)

        Returns:
            해당 본명성의 기본석 PowerStone
        """

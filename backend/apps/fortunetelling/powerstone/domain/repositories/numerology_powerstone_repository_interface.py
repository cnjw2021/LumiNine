"""INumerologyPowerStoneRepository — 수비술 파워스톤 데이터 접근 인터페이스."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict

from apps.fortunetelling.powerstone.domain.value_objects.numerology_powerstone import NumerologyStone


class INumerologyPowerStoneRepository(ABC):
    """수비술 파워스톤 카탈로그 데이터 접근 도메인 포트.

    구현체는 Infrastructure 레이어에 위치하며,
    numerology_powerstone_catalog.json 기반 정적 데이터를 로드한다.
    """

    @abstractmethod
    def get_stone(self, stone_id: str) -> NumerologyStone:
        """스톤 ID로 단일 스톤 정보 반환.

        Args:
            stone_id: 스톤 고유 식별자

        Returns:
            NumerologyStone

        Raises:
            ValueError: 존재하지 않는 stone_id
        """

    @abstractmethod
    def get_mapping(self, number: int) -> Dict:
        """수비술 숫자에 대한 레이어별 매핑 반환.

        Life Path Number 및 Personal Year Number 조회에 공용으로 사용된다.

        Args:
            number: 수비술 숫자 (1~9 또는 11/22/33)

        Returns:
            {"planet": str, "overall": {...}, "health": {...},
             "wealth": {...}, "love": {...}, "yearly": {...}}

        Raises:
            ValueError: 유효 범위 밖의 숫자
        """

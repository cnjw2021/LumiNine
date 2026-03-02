"""Domain port interface for the monthly-board (月盤) assembly service."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Protocol


class IMonthlyBoardDomainService(Protocol):
    """월반(月盤) 편성(組立) 서비스의 도메인 포트.

    구체적인 구현은 Infrastructure 레이어(또는 서비스 레이어)에 위치하며,
    이 인터페이스를 통해 Use Case 레이어에서 의존성을 역전시킨다.
    """

    def get_monthly_board(
        self,
        target_date: date,
        year_center_star: int,
        year_zodiac: str,
    ) -> "MonthlyBoardResult":
        """주어진 날짜에 해당하는 월반(月盤) 결과를 반환한다.

        Args:
            target_date: 방위를 조회할 기준 날짜 (절입일 경계를 포함해 판정)
            year_center_star: 해당 연도의 연반 중궁성 (1~9)
            year_zodiac: 해당 연도의 연간지 문자열 (예: '甲子')

        Returns:
            MonthlyBoardResult 인스턴스
        """
        ...


# 순환 임포트를 피하기 위해 TYPE_CHECKING 블록 없이 직접 import 가능하도록
# MonthlyBoardResult는 monthly_board_domain_service 모듈에 정의한다.
from apps.ninestarki.domain.services.monthly_board_domain_service import MonthlyBoardResult  # noqa: E402, F401
